from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "typed_aligned_batch_mitm.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "typed_aligned_batch_mitm_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load aligned-batch module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedAlignedBatchMitmTests(unittest.TestCase):
    def test_target_sizes_deduplicate(self) -> None:
        records = MODULE.target_sizes(5, [0.5, 1.0, 1.5])
        self.assertEqual([record["size"] for record in records], [3, 5, 12])

    def test_quotient_coefficients(self) -> None:
        self.assertEqual(
            MODULE.quotient_coefficients(-2, (0, 1, 1, 3), 4),
            [1, -2, 2, 0, 1],
        )

    def test_small_aligned_key_bound(self) -> None:
        curve = MODULE.TYPED.Curve(17, 2, 2)
        generator = (5, 1)
        p0 = curve.mul(2, generator)
        d_point = curve.mul(3, generator)
        q0 = curve.mul(4, generator)
        r_points = [
            curve.mul(5, generator),
            curve.mul(6, generator),
        ]
        record = MODULE.build_aligned_keys(
            curve, 19, q0, p0, d_point, r_points, 3, 4
        )
        self.assertEqual(record["summary"]["target_records"], 12)
        self.assertEqual(
            record["summary"]["target_records"],
            record["summary"]["theoretical_record_bound"],
        )

    def test_d2_retains_canonical_pairs(self) -> None:
        curve = MODULE.TYPED.Curve(17, 2, 2)
        generator = (5, 1)
        r_points = [
            curve.mul(value, generator) for value in (1, 2, 3)
        ]
        d2 = MODULE.build_d2(curve, r_points)
        self.assertEqual(d2["summary"]["attempted_transitions"], 6)
        self.assertEqual(d2["summary"]["witness_records"], 6)


if __name__ == "__main__":
    unittest.main()
