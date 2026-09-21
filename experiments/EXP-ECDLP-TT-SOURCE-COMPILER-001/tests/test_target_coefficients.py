from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from types import ModuleType


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = EXPERIMENT_DIR / "src" / "tt_target_coefficients.py"
TARGET_MANIFEST = EXPERIMENT_DIR / "target-instance-manifest-v1.json"


def load_module() -> ModuleType:
    specification = importlib.util.spec_from_file_location(
        "tt_target_coefficients",
        MODULE_PATH,
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("unable to load target coefficient module")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class TargetCoefficientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.manifest = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))[
            "target_manifest"
        ]

    def test_every_frozen_trace_zero_vector(self) -> None:
        for instance in self.manifest["instances"]:
            p = instance["p"]
            n = instance["trace_zero_norm_n"]
            for target_name, target in instance["targets"].items():
                with self.subTest(curve=instance["curve_id"], target=target_name):
                    observed = self.module.trace_zero_coefficients(
                        target["projective"],
                        p,
                        n,
                    )
                    self.assertEqual(observed, tuple(target["trace_zero_coefficients"]))

    def test_every_frozen_general_basis_vector(self) -> None:
        for instance in self.manifest["instances"]:
            control = instance["general_trace_control"]
            target = instance["targets"]["Q00"]
            with self.subTest(curve=instance["curve_id"]):
                observed = self.module.general_basis_coefficients(
                    target["projective"],
                    instance["p"],
                    control["trace_t"],
                    control["norm_n"],
                )
                self.assertEqual(observed, tuple(target["general_trace_coefficients"]))

    def test_identity_retains_the_n_y_squared_term(self) -> None:
        for instance in self.manifest["instances"]:
            p = instance["p"]
            n = instance["trace_zero_norm_n"]
            with self.subTest(curve=instance["curve_id"]):
                self.assertEqual(
                    self.module.trace_zero_coefficients((0, 1, 0), p, n),
                    (0, 0, n, 0, 0, 0),
                )

    def test_coefficients_are_projectively_quadratic(self) -> None:
        for instance in self.manifest["instances"]:
            p = instance["p"]
            n = instance["trace_zero_norm_n"]
            target = instance["targets"]["Q00"]["projective"]
            scale = 7 % p
            scaled_target = tuple(scale * coordinate % p for coordinate in target)
            expected_scale = scale * scale % p
            original = self.module.trace_zero_coefficients(target, p, n)
            scaled = self.module.trace_zero_coefficients(scaled_target, p, n)
            self.assertEqual(
                scaled,
                tuple(expected_scale * coefficient % p for coefficient in original),
            )


if __name__ == "__main__":
    unittest.main()
