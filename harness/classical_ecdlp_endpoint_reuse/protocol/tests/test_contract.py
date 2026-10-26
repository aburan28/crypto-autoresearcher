#!/usr/bin/env python3
"""Deterministic synthetic interface checks, never confirmation measurements."""
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

analysis = module("analysis")
seeds = module("seed_rules")
exporter = module("export_bundle")

class Contracts(unittest.TestCase):
    def test_one_group_counter_is_not_nested_sum(self):
        value = analysis.add_vectors({"group_additions": 13, "scalar_multiplications": 2},
                                     {"group_additions": 7, "scalar_multiplications": 1})
        self.assertEqual(value, {"group_additions": 20, "scalar_multiplications": 3})

    def test_negative_boolean_and_missing_counters_refused(self):
        for value in ({"group_additions": -1}, {"group_additions": True}, {"scalar_multiplications": 2}):
            with self.assertRaises(ValueError):
                analysis.exact_counters(value)

    def test_constant_ratio_bootstrap_has_exact_scope(self):
        result = analysis.cluster_summary([.5] * 4, [[0, 1, 2, 3], [3, 3, 3, 3]])
        self.assertEqual(result["curves"], 4)
        self.assertAlmostEqual(result["gmean_ratio"], .5)
        self.assertEqual(result["pointwise_cluster_bootstrap_ci95"], [.5, .5])

    def test_gmean_uses_equal_curve_weight(self):
        result = analysis.cluster_summary([.25, 4.], [[0, 1]])
        self.assertAlmostEqual(result["gmean_ratio"], 1.)
        self.assertEqual(result["curve_ratio_range"], [.25, 4.])

    def test_no_ratio_floor(self):
        with self.assertRaises(ValueError):
            analysis.cluster_summary([0., 1.], [[0, 1]])

    def test_seed_is_shared_by_arm_because_arm_is_not_an_argument(self):
        args = ("0" * 64, "test-nonce-not-real-entropy", "fixture-test", 0, "solver_cell")
        self.assertEqual(seeds.public_seed(*args), seeds.public_seed(*args))
        self.assertNotEqual(seeds.public_seed(*args), seeds.public_seed(*args[:-1], "arm_order"))
        self.assertNotEqual(seeds.public_seed(*args), seeds.public_seed(*args[:3], 1, args[4]))

    def test_cap_formula_is_integer_and_requested_chains(self):
        t, c0, cap = seeds.table_parameters(2141)
        self.assertEqual((t, c0, cap), (4, 8, 32))

    def test_analysis_parts_are_bounded_and_lossless(self):
        rows = [{"index": i, "payload": "x" * 70} for i in range(20)]
        import json
        with tempfile.TemporaryDirectory() as tmp:
            parts = analysis.write_parts(Path(tmp), rows, byte_limit=512)
            recovered = []
            for part in parts:
                path = Path(tmp) / part["path"]
                self.assertLessEqual(path.stat().st_size, 512)
                recovered.extend(json.loads(path.read_text()))
            self.assertEqual(recovered, rows)

    def test_export_keeps_native_sequences_not_a_fake_price(self):
        rows = [{"row_kind": "target", "counters": {"group_additions": 3, "scalar_multiplications": 1},
                 "rng": {"word_draws": 4}, "pending_count": 2},
                {"row_kind": "target", "counters": {"group_additions": 5, "scalar_multiplications": 2},
                 "rng": {"word_draws": 6}, "pending_count": 0}]
        actual = exporter.counter_sequences(rows)
        self.assertEqual(actual["native.target.counters.group_additions"], "[3,5]")
        self.assertEqual(actual["native.target.counters.scalar_multiplications"], "[1,2]")
        self.assertEqual(actual["native.target.rng.word_draws"], "[4,6]")
        self.assertEqual(actual["native.target.state.pending_count"], "[2,0]")

    def test_export_partial_target_count_does_not_invent_m64(self):
        rows = [{"row_kind": "setup", "counters": {"group_additions": 10}},
                {"row_kind": "target", "target_ordinal": 0, "status": "censored", "verified_scalar": None,
                 "counters": {"group_additions": 4}}]
        actual = exporter.target_metrics(rows)
        self.assertEqual(actual["observed_target_cases"], 1)
        self.assertEqual(actual["group_additions_m1"], 14)
        self.assertNotIn("group_additions_m64", actual)
        self.assertNotIn("verified_targets_m64", actual)

if __name__ == "__main__":
    unittest.main()
