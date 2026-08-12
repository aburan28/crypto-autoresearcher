from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "typed_five_term.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "typed_five_term_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load typed-five-term module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedFiveTermTests(unittest.TestCase):
    def test_optimizer_meets_occupancy(self) -> None:
        a, r = MODULE.choose_sizes(1009, 0.5)
        self.assertGreaterEqual(
            a * MODULE.math.comb(r + 3, 4) / 1009, 0.5
        )

    def test_layers_are_disjoint(self) -> None:
        a, r, _ = MODULE.build_layers(101, 4, 5, 12345)
        self.assertFalse(a & r)
        self.assertNotIn(0, a)
        self.assertNotIn(0, r)

    def test_exact_split_geometry(self) -> None:
        a, r, _ = MODULE.build_layers(101, 4, 5, 12345)
        result = MODULE.geometry(a, r, 101)
        self.assertGreater(result["d5_nonidentity"], 0)
        self.assertGreaterEqual(result["split_redundancy"], 1)
        self.assertEqual(result["log_unknowns"], len(r) + 2)


if __name__ == "__main__":
    unittest.main()
