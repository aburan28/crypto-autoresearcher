from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "mixed_layer.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "mixed_layer_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load mixed-layer module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class MixedLayerTests(unittest.TestCase):
    def test_builder_has_exact_disjoint_layers(self) -> None:
        record = MODULE.build_mixed_base(101, 8, 0.5, 12345)
        self.assertEqual(len(record["base"]), 8)
        self.assertFalse(
            set(record["core"]) & set(record["progression"])
        )
        self.assertNotIn(0, record["base"])

    def test_progression_control_compresses_early_support(self) -> None:
        progression = MODULE.build_mixed_base(101, 8, 0.0, 12345)
        random_base = MODULE.build_random_base(101, 8, 12345)
        progression_geometry = MODULE.geometry(progression["base"], 101)
        random_geometry = MODULE.geometry(random_base, 101)
        self.assertLess(
            progression_geometry["d2"], random_geometry["d2"]
        )
        self.assertLess(
            progression_geometry["d3"], random_geometry["d3"]
        )

    def test_tiny_cell_reports_every_fraction(self) -> None:
        cell = MODULE.run_cell(
            101, 0.5, [0.0, 0.5, 1.0], 3, 12345
        )
        self.assertEqual(len(cell["families"]), 3)
        self.assertTrue(
            all(len(family["draws"]) == 3 for family in cell["families"])
        )


if __name__ == "__main__":
    unittest.main()
