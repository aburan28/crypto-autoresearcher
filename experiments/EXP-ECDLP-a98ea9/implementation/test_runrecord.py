"""Regression checks for archived-run manifest serialization."""

import unittest

import yaml

from runrecord import _dump_yaml


class RunRecordYamlTests(unittest.TestCase):
    def test_multiline_git_status_roundtrips_as_one_string(self):
        manifest = {
            "run_id": "RUN-ECDLP-a98ea9-control",
            "git": {
                "dirty": True,
                "dirty_summary": " M implementation/stage2.py\n?? runs/RUN-S2/",
            },
            "validity": {"status": "valid"},
        }

        self.assertEqual(yaml.safe_load(_dump_yaml(manifest)), manifest)

    def test_string_values_keep_their_types(self):
        value = {"number_text": "12", "boolean_text": "false", "empty": ""}

        self.assertEqual(yaml.safe_load(_dump_yaml(value)), value)


if __name__ == "__main__":
    unittest.main()
