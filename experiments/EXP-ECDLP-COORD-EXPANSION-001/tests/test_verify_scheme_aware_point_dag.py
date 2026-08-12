from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_scheme_aware_point_dag.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_scheme_aware_point_dag_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load point DAG verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifySchemeAwarePointDagTests(unittest.TestCase):
    def test_independent_cycle_degrees(self) -> None:
        cycles, d2_support = MODULE.reconstruct_cycles(
            [(3, 6), (80, 10)], 97, 2
        )
        self.assertEqual(
            sum(record[0] for record in cycles["canonical"].values()),
            5,
        )
        self.assertEqual(
            sum(record[0] for record in cycles["ordered"].values()),
            16,
        )
        self.assertEqual(
            sum(
                record[0]
                for record in cycles["unique_d2_pair"].values()
            ),
            MODULE.math.comb(d2_support + 1, 2),
        )

    def test_independent_characteristic_roots(self) -> None:
        p, delta = 97, 5
        roots = [(3, 6), (80, 10), (3, 6)]
        polynomial = MODULE.characteristic(roots, p, delta)
        self.assertTrue(
            all(
                MODULE.polynomial_eval(
                    polynomial, root, p, delta
                )
                == (0, 0)
                for root in roots
            )
        )


if __name__ == "__main__":
    unittest.main()
