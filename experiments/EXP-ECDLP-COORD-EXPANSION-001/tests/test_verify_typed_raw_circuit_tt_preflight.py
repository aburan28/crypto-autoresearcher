from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "src" / "verify_typed_raw_circuit_tt_preflight.py"


def load_module():
    spec = importlib.util.spec_from_file_location("verify_raw_circuit_tt_under_test", SOURCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load raw circuit TT verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class VerifyTypedRawCircuitTtPreflightTests(unittest.TestCase):
    def test_expected_shape_is_rank_one(self) -> None:
        self.assertEqual(MODULE.expected_shape(), [1, 1, 1, 1, 1, 1])


if __name__ == "__main__":
    unittest.main()
