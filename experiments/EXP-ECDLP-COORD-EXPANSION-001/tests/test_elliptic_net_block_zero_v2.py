from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "elliptic_net_block_zero_v2.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "elliptic_net_block_zero_v2_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load normalized block-zero module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class EllipticNetBlockZeroV2Tests(unittest.TestCase):
    def test_normalization_removes_projective_scale(self) -> None:
        output = (7, 11, 1)
        target = (3, 5)
        values = [
            MODULE.normalized_locator_value(
                tuple(coordinate * scale % 101 for coordinate in output),
                target,
                101,
                2,
            )
            for scale in (1, 2, 3, 5)
        ]
        self.assertEqual(len(set(values)), 1)

    def test_normalization_zero_is_exact_for_affine_target(self) -> None:
        output = MODULE.BASE.NORM.affine_to_projective((3, 5))
        self.assertEqual(
            MODULE.normalized_locator_value(output, (3, 5), 101, 2), 0
        )

    def test_infinity_is_nonzero_sentinel(self) -> None:
        self.assertNotEqual(
            MODULE.normalized_locator_value((1, 0, 0), (3, 5), 101, 2), 0
        )


if __name__ == "__main__":
    unittest.main()
