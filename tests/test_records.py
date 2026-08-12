from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import (
    RecordValidationError,
    find_repo_root,
    validate_instance,
    validate_record,
)


REPO_ROOT = find_repo_root(Path(__file__).parent)


class RecordTests(unittest.TestCase):
    def test_checked_in_experiment_records_validate(self) -> None:
        root = REPO_ROOT / "experiments" / "EXP-ECDLP-ENERGY-001"
        expected = {
            "research-question.json": "research_question",
            "hypothesis.json": "hypothesis",
            "specification.json": "experiment",
            "handoff.json": "handoff",
        }
        for name, kind in expected.items():
            with self.subTest(name=name):
                self.assertEqual(validate_record(root / name, REPO_ROOT), kind)

    def test_integer_schema_rejects_boolean_and_float(self) -> None:
        schema = {"type": "integer", "minimum": 0}
        for value in (False, True, 0.0, 1.0):
            with self.subTest(value=value):
                with self.assertRaises(RecordValidationError):
                    validate_instance(value, schema)

    def test_unknown_top_level_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "record.json"
            path.write_text(json.dumps({"unknown": {}}), encoding="utf-8")
            with self.assertRaises(RecordValidationError):
                validate_record(path, REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
