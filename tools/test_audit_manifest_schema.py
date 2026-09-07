import copy
import json
from pathlib import Path
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / "schemas/run-manifest.schema.json").read_text())
        self.record = json.loads((ROOT / "experiments/EXP-PFDR-845d33/corrections/RUN-PFDR-20260906-eb1a30.v2.yaml").read_text())

    def test_archived_normalized_failures_are_representable(self):
        for p in (ROOT / "experiments/EXP-PFDR-845d33/corrections").glob("*.v2.yaml"):
            jsonschema.validate(json.loads(p.read_text()), self.schema)

    def test_success_requires_measured_resources(self):
        self.record["run"]["status"] = "completed_valid"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.record, self.schema)

    def test_certificate_claim_requires_verification(self):
        self.record["run"]["result"]["certificate"]["kind"] = "discrete_log"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.record, self.schema)

    def test_ids_are_anchored_and_accept_random_suffix(self):
        jsonschema.validate(self.record, self.schema)
        self.record["run"]["experiment_id"] += "-garbage"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.record, self.schema)

    def test_missing_certificate_is_not_silently_accepted(self):
        del self.record["run"]["result"]["certificate"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.record, self.schema)


if __name__ == "__main__":
    unittest.main()
