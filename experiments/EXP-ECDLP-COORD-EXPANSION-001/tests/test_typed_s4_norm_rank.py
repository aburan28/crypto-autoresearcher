from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "typed_s4_norm_rank.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "typed_s4_norm_rank_under_test", SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load typed S4 norm-rank module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class TypedS4NormRankTests(unittest.TestCase):
    def test_flat_index(self) -> None:
        shape = [2, 3, 4]
        self.assertEqual(MODULE.flat_index((0, 0, 0), shape), 0)
        self.assertEqual(MODULE.flat_index((1, 2, 3), shape), 23)

    def test_rank_mod_separable_and_dense(self) -> None:
        shape = [3, 4, 2]
        separable = [
            (i + 1) * (j + 2) * (k + 3) % 101
            for i in range(3)
            for j in range(4)
            for k in range(2)
        ]
        self.assertEqual(
            MODULE.rank_mod(separable, shape, 1, 101)["rank"], 1
        )
        dense = [
            int.from_bytes(
                MODULE.hashlib.sha256(
                    f"{i}|{j}|{k}".encode("ascii")
                ).digest(),
                "big",
            )
            % 101
            for i in range(3)
            for j in range(4)
            for k in range(2)
        ]
        self.assertGreaterEqual(
            MODULE.rank_mod(dense, shape, 1, 101)["rank"], 2
        )

    def test_runtime_rank_controls(self) -> None:
        controls = MODULE.rank_controls()
        self.assertTrue(controls["all_expected"])
        for name in ("rank_one_separable", "single_spike"):
            self.assertTrue(
                all(
                    record["rank"] == 1
                    for record in controls["records"][name]
                )
            )
        self.assertTrue(
            all(
                record["rank"] == record["ambient_rank"]
                for record in controls["records"][
                    "deterministic_dense_hash"
                ]
            )
        )

    def test_nonsquare(self) -> None:
        value = MODULE.nonsquare(101)
        self.assertEqual(pow(value, 50, 101), 100)

    def test_tiny_source_and_locator(self) -> None:
        curve = MODULE.TYPED_EC.Curve(17, 2, 2)
        generator = (5, 1)
        a_points = [
            curve.mul(value, generator) for value in (1, 2)
        ]
        r_points = [
            curve.mul(value, generator) for value in (3, 5)
        ]
        source = MODULE.tensor_source(
            17, 2, 2, a_points, r_points
        )
        target = MODULE.sum_affine(
            [a_points[0], r_points[0], r_points[0], r_points[1], r_points[1]],
            17,
            2,
        )
        locator = MODULE.locator_tensors(
            source, target, 17, MODULE.nonsquare(17), [1, 2, 8]
        )
        self.assertEqual(source["summary"]["invalid_projective_count"], 0)
        self.assertEqual(source["summary"]["affine_replay_mismatches"], 0)
        self.assertEqual(locator["summary"]["zero_set_mismatches"], 0)
        self.assertGreaterEqual(locator["summary"]["witness_count"], 1)


if __name__ == "__main__":
    unittest.main()
