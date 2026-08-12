from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "scheme_aware_point_dag.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "scheme_aware_point_dag_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load point DAG module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class SchemeAwarePointDagTests(unittest.TestCase):
    def test_cycle_degrees_and_support(self) -> None:
        points = [(3, 6), (80, 10)]
        cycles, build = MODULE.build_cycles(points, 97, 2)
        self.assertEqual(
            sum(
                record["multiplicity"]
                for record in cycles["canonical"].values()
            ),
            5,
        )
        self.assertEqual(
            sum(
                record["multiplicity"]
                for record in cycles["ordered"].values()
            ),
            16,
        )
        self.assertEqual(
            sum(
                record["multiplicity"]
                for record in cycles["unique_d2_pair"].values()
            ),
            MODULE.math.comb(build["d2_support"] + 1, 2),
        )
        self.assertEqual(
            set(cycles["canonical"]),
            set(cycles["ordered"]),
        )

    def test_fp2_product_roots(self) -> None:
        p = 97
        delta = MODULE.nonsquare(p)
        roots = [(3, 6), (80, 10), (3, 6)]
        polynomial, _ = MODULE.product_tree(roots, p, delta)
        for root in roots:
            self.assertEqual(
                MODULE.poly_eval(
                    polynomial,
                    root,
                    p,
                    delta,
                    MODULE.Fp2Counter(),
                ),
                (0, 0),
            )

    def test_oriented_encoding_distinguishes_sign(self) -> None:
        self.assertNotEqual(
            MODULE.encode_oriented((3, 6)),
            MODULE.encode_oriented((3, 91)),
        )


if __name__ == "__main__":
    unittest.main()
