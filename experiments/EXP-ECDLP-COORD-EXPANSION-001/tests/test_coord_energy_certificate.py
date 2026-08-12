from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "coord_energy_certificate.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "coord_energy_certificate_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load coordinate energy source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class CoordinateEnergyCertificateTests(unittest.TestCase):
    def test_scalar_progression_has_full_ap_cover(self) -> None:
        metrics = MODULE.set_metrics([3, 8, 13, 18, 23], 101)
        self.assertEqual(
            metrics["best_length_b_progression"]["cover"], 5
        )
        self.assertEqual(metrics["d2"]["representation_total"], 25)
        self.assertEqual(metrics["d4"]["representation_total"], 625)

    def test_fourier_normalization_is_bounded(self) -> None:
        value = MODULE.max_fourier_normalized((1, 4, 9, 16), 101)
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 1.0)

    def test_predictor_never_uses_scalar_feature(self) -> None:
        training = [
            {
                "features": {"x_bin_8": str(index % 2)},
                "multiplicity": index + 1,
                "positive": index >= 4,
            }
            for index in range(8)
        ]
        result = MODULE.fit_predictor(training, training)
        self.assertFalse(result["uses_scalar_feature"])
        self.assertEqual(result["feature"], "x_bin_8")


if __name__ == "__main__":
    unittest.main()
