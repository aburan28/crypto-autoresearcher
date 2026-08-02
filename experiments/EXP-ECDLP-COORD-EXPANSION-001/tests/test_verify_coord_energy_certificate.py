from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_coord_energy_certificate.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_coord_energy_certificate_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load energy verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyCoordinateEnergyCertificateTests(unittest.TestCase):
    def test_direct_d4_representation_total(self) -> None:
        values = (2, 7, 12, 17)
        counts = MODULE.d4_counts(values, 101)
        self.assertEqual(sum(counts.values()), len(values) ** 4)

    def test_independent_progression_cover(self) -> None:
        cover, _, _ = MODULE.progression_cover(
            (3, 8, 13, 18, 23), 101
        )
        self.assertEqual(cover, 5)

    def test_predictor_has_no_scalar_feature(self) -> None:
        rows = [
            {
                "features": {"x_bin_8": str(index % 2)},
                "multiplicity": index + 1,
                "positive": index >= 4,
            }
            for index in range(8)
        ]
        result = MODULE.independent_fit(rows, rows)
        self.assertFalse(result["uses_scalar_feature"])


if __name__ == "__main__":
    unittest.main()
