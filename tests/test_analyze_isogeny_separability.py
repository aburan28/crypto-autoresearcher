import json
import tempfile
import unittest
from pathlib import Path
from tools.analyze_isogeny_separability import summarize

class TestSummary(unittest.TestCase):
    def test_receipt_summary(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"receipt.jsonl"
            path.write_text("\n".join(map(json.dumps, [
                {"kind":"frobenius","homomorphism_verified":True},
                {"kind":"edge_search","edge_count":1},
                {"kind":"odd_isogeny","ell":3,"homomorphism_verified":True}
            ]))+"\n")
            result = summarize(path)
            self.assertEqual(result["records"],3)
            self.assertEqual(result["odd_edge_degrees"],[3])
            self.assertFalse(result["conductor_gap_verified"])
            self.assertFalse(result["ecdlp_cost_separation_measured"])

if __name__ == "__main__":
    unittest.main()
