from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "verify_direct_equality_pair_coefficients_strict.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "verify_coefficients_strict_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load strict coefficient verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyCoefficientStrictTests(unittest.TestCase):
    def test_recorded_cut_valid_rejects_bad_mutation(self) -> None:
        cut = {
            "coordinate_digest_matches_v1": True,
            "basis_dimension": 24,
            "degree": 8,
            "targets": {"planted": {"matches_v1": True}},
            "witness_checks": {
                "planted": {
                    "present": True,
                    "residual_zero": True,
                    "affine_output_matches": True,
                    "mutated_target_residual_nonzero": False,
                }
            },
            "coefficient_mutation_control": {
                "digest_changed": True,
                "evaluation_changed": True,
            },
        }
        self.assertFalse(MODULE.recorded_cut_valid(cut))


if __name__ == "__main__":
    unittest.main()
