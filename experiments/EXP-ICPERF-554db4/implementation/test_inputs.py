"""Focused mutation and point-permutation controls for sorted m8 inputs."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


producer = module("encode_sorted")
checker = module("verify_inputs")


class SortedInputsTest(unittest.TestCase):
    def test_comparator_boundaries_and_mutant(self) -> None:
        # Gate semantics are checked on both equality and strict ordering.
        for left, right in ((0, 0), (0, 1), (1, 0), (2047, 2047),
                            (2046, 2047), (2047, 2046), (1024, 1023)):
            circuit = producer.Circuit(2 * producer.WIDTH)
            gate = producer.greater(circuit, 0, 1)
            values = producer.evaluate_nodes(circuit, left | right << producer.WIDTH)
            self.assertEqual(bool(values[gate]), left > right)

    def test_serialized_inputs_and_full_points(self) -> None:
        result = checker.verify()
        self.assertEqual(set(result["controls"]), {"weighted", "local_random"})
        for row in result["controls"].values():
            self.assertTrue(row["sorted_model_complete"])
            self.assertTrue(row["reversed_sorted_order_rejected"])
            self.assertTrue(row["first_primary_bit_flip_rejected"])
            self.assertGreaterEqual(row["constructed_controls"]["opposite_sign"]["ties"], 2)

    def test_sorted_primary_mutation_rejected(self) -> None:
        manifest = json.loads(checker.MANIFEST.read_bytes())
        row = manifest["arms"]["weighted"]
        raw = checker.gzip.decompress((checker.ROOT / row["formula_path"]).read_bytes())
        bits = int(row["sorted_primary_hex"], 16)
        with self.assertRaises(ValueError):
            checker.full_values(raw, bits ^ 1, row["live_gates"])


if __name__ == "__main__":
    unittest.main()
