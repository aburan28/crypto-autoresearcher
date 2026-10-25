"""Fixed comparator regressions only; no recorded research command is launched."""
import importlib.util
import json
from pathlib import Path
import unittest

from exact_comparison import compare_results

HERE = Path(__file__).resolve().parent


class ExactComparisonTests(unittest.TestCase):
    def test_preserves_original_counterexample(self):
        record = json.loads((HERE / "20261019-replay-comparison.json").read_text())
        old_path = HERE.parent / "scripts/replay.py"
        spec = importlib.util.spec_from_file_location("archived_replay", old_path)
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        left, right = record["counterexample"]["expected"], record["counterexample"]["actual"]
        self.assertNotEqual(left, right)
        self.assertEqual(old.strip(left), old.strip(right))
        self.assertFalse(compare_results(left, right)["equal"])

    def test_scientific_names_are_never_inferred_to_be_metadata(self):
        for key in ("candidate_scalar", "candidate_point", "direction", "runtime_bound"):
            with self.subTest(key=key):
                self.assertFalse(compare_results({key: 7}, {key: 19})["equal"])

    def test_small_floats_remain_distinct(self):
        self.assertFalse(compare_results({"value": 1e-10}, {"value": 2e-10})["equal"])

    def test_boolean_is_not_an_integer(self):
        self.assertFalse(compare_results({"accepted": True}, {"accepted": 1})["equal"])

    def test_integer_and_float_types_are_preserved(self):
        self.assertFalse(compare_results({"value": 1}, {"value": 1.0})["equal"])

    def test_list_order_and_length(self):
        self.assertFalse(compare_results([1, 2], [2, 1])["equal"])
        self.assertFalse(compare_results([1, 2], [1])["equal"])

    def test_only_exact_reviewed_path_is_ignored(self):
        left = {"metadata": {"timestamp": "a"}, "result": {"timestamp": "x"}}
        right = {"metadata": {"timestamp": "b"}, "result": {"timestamp": "x"}}
        result = compare_results(left, right, ignored_metadata_paths=(("metadata", "timestamp"),))
        self.assertTrue(result["equal"])
        self.assertEqual(result["ignored_metadata_paths"], [["metadata", "timestamp"]])
        right["result"]["timestamp"] = "changed"
        self.assertFalse(compare_results(left, right, ignored_metadata_paths=(("metadata", "timestamp"),))["equal"])

    def test_missing_metadata_is_refused(self):
        with self.assertRaises(ValueError):
            compare_results({"timestamp": "a"}, {}, ignored_metadata_paths=(("timestamp",),))

    def test_container_and_root_ignores_are_refused(self):
        for path in ((), ("result",)):
            with self.subTest(path=path), self.assertRaises(ValueError):
                compare_results({"result": {}}, {"result": {}}, ignored_metadata_paths=(path,))

    def test_nonfinite_values_are_refused(self):
        for number in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(number=number), self.assertRaises(ValueError):
                compare_results({"value": number}, {"value": number})

    def test_missing_scientific_field_is_a_difference(self):
        self.assertFalse(compare_results({"candidate_scalar": 7}, {})["equal"])

    def test_unchanged_json_is_equal(self):
        value = {"candidate_scalar": 7, "candidate_point": [1, 2], "ok": True, "cost": None}
        self.assertTrue(compare_results(value, value)["equal"])

    def test_invalid_metadata_path_type_is_refused(self):
        with self.assertRaises(ValueError):
            compare_results({}, {}, ignored_metadata_paths=("timestamp",))


if __name__ == "__main__":
    unittest.main()
