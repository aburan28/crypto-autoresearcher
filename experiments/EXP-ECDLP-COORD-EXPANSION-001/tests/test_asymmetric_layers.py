from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "asymmetric_layers.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "asymmetric_layers_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load asymmetric-layers module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class AsymmetricLayerTests(unittest.TestCase):
    def test_size_optimizer_meets_occupancy(self) -> None:
        a, r = MODULE.choose_layer_sizes(1009, 0.5)
        occupancy = (2 * a - 1) * MODULE.math.comb(r + 2, 3) / 1009
        self.assertGreaterEqual(occupancy, 0.5)

    def test_layers_are_disjoint_and_nonidentity(self) -> None:
        a, r, _ = MODULE.build_layers(101, 4, 6, 12345)
        self.assertFalse(a & r)
        self.assertNotIn(0, a)
        self.assertNotIn(0, r)

    def test_split_support_is_exact(self) -> None:
        a, r, _ = MODULE.build_layers(101, 4, 6, 12345)
        result = MODULE.layer_geometry(a, r, 101)
        self.assertGreater(result["d5"], 0)
        self.assertGreaterEqual(result["split_redundancy"], 1)


if __name__ == "__main__":
    unittest.main()
