from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "cyclic_pareto.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "cyclic_pareto_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load cyclic Pareto module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class CyclicParetoTests(unittest.TestCase):
    def test_support_levels_match_direct_sum_meaning(self) -> None:
        levels = MODULE.support_levels((1, 4, 7), 11)
        self.assertEqual(levels[1], {1, 4, 7})
        self.assertEqual(
            levels[2],
            {(left + right) % 11 for left in levels[1] for right in levels[1]},
        )
        self.assertEqual(
            levels[5],
            {
                (left + right) % 11
                for left in levels[2]
                for right in levels[3]
            },
        )

    def test_sign_complete_enumerator_builds_inverse_pairs(self) -> None:
        for base in MODULE.bases(11, 4, "sign_complete"):
            self.assertEqual((base[0] + base[1]) % 11, 0)
            self.assertEqual((base[2] + base[3]) % 11, 0)

    def test_pareto_frontier_removes_dominated_tuple(self) -> None:
        frontier = MODULE.pareto_frontier(
            {(4, 6, 10), (5, 7, 9), (3, 8, 11)}
        )
        self.assertIn((4, 6, 10), frontier)
        self.assertIn((3, 8, 11), frontier)
        self.assertNotIn((5, 7, 9), frontier)

    def test_tiny_exhaustive_cell_is_consistent(self) -> None:
        cell = MODULE.analyze_cell(11, 0.5, "sign_complete")
        self.assertEqual(
            cell["sets_enumerated"],
            len(list(MODULE.bases(11, cell["factor_base_size"], "sign_complete"))),
        )
        self.assertGreater(cell["unique_metric_tuples"], 0)
        self.assertGreater(len(cell["pareto_frontier"]), 0)

    def test_weighted_median_matches_expanded_values(self) -> None:
        counts = {(1, 2, 3, 4): 2, (5, 6, 7, 8): 1}
        self.assertEqual(MODULE.weighted_median(counts, 0), 1)
        self.assertEqual(MODULE.weighted_median(counts, 3), 4)

    def test_scaling_normal_form_is_scale_invariant(self) -> None:
        base = (1, 4, 7, 38)
        scaled = tuple((3 * value) % 43 for value in base)
        self.assertEqual(
            MODULE.scaling_normal_form(base, 43),
            MODULE.scaling_normal_form(scaled, 43),
        )


if __name__ == "__main__":
    unittest.main()
