from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "typed_raw_circuit_tt_preflight.py"


def load_module():
    spec = importlib.util.spec_from_file_location("raw_circuit_tt_under_test", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load raw circuit TT module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedRawCircuitTtPreflightTests(unittest.TestCase):
    def test_shape_rules(self) -> None:
        left = [1, 2, 3, 4, 5, 1]
        right = [1, 7, 11, 13, 17, 1]
        self.assertEqual(MODULE.add_shape(left, right), [1, 9, 14, 17, 22, 1])
        self.assertEqual(MODULE.multiply_shape(left, right), [1, 14, 33, 52, 85, 1])

    def test_rank_one_controls(self) -> None:
        shape = MODULE.variable_shapes(0)[0]
        self.assertEqual(shape, [1, 1, 1, 1, 1, 1])
        self.assertEqual(MODULE.raw_core_entries(shape, 5), 25)


if __name__ == "__main__":
    unittest.main()
