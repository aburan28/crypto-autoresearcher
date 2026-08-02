from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "typed_two_dimensional_lattice.py"


def load_module():
    spec = importlib.util.spec_from_file_location("two_dimensional_lattice_under_test", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load lattice module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedTwoDimensionalLatticeTests(unittest.TestCase):
    def test_lattice_coefficients_include_second_direction(self) -> None:
        self.assertEqual(MODULE.lattice_coefficients(3, 2, (0, 1, 1, 2), 4), [1, -3, -2, 2, 1, 0])

    def test_small_key_bound(self) -> None:
        curve = MODULE.ALIGNED.TYPED.Curve(17, 2, 2)
        generator = (5, 1)
        points = [curve.mul(value, generator) for value in (1, 2)]
        record = MODULE.build_lattice_keys(curve, 19, points[0], points[0], points[1], generator, points, 2, 3, 2)
        self.assertEqual(record["summary"]["target_records"], 16)
        self.assertEqual(record["summary"]["target_records"], record["summary"]["theoretical_record_bound"])


if __name__ == "__main__":
    unittest.main()
