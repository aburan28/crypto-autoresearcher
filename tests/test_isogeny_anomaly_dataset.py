import json
import tempfile
import unittest
from pathlib import Path
from tools.isogeny_anomaly_dataset import assemble, validate

class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.row = {"curve_id":"test:1","family":"binary","field":{"characteristic":"2","degree":83},"order":"123","features":{"trace":"7"},"provenance":{"revision":"abc","generator":"test","parameters":{}}}
    def test_valid(self):
        self.assertEqual(validate(self.row), self.row)
    def test_missing_provenance(self):
        row = dict(self.row, provenance={})
        with self.assertRaises(ValueError):
            validate(row)
    def test_conflicting_ids(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, out = (Path(d)/x for x in ("a.jsonl","b.jsonl","out.jsonl"))
            a.write_text(json.dumps(self.row)+"\n")
            b.write_text(json.dumps(dict(self.row, order="999"))+"\n")
            with self.assertRaises(ValueError):
                assemble([a,b],out)
    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            a, out = Path(d)/"a.jsonl", Path(d)/"out.jsonl"
            a.write_text(json.dumps(self.row)+"\n"+json.dumps(self.row)+"\n")
            result = assemble([a],out)
            self.assertEqual(result["records"],1)
            self.assertEqual(len(result["sha256"]),64)

if __name__ == "__main__":
    unittest.main()
