import unittest
from tools.validate_crypto_ml import validate

class CryptoMLValidationTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            "schema_version":"crypto-ml-v1",
            "experiment":{"id":"toy","task":"binary_distinguisher"},
            "primitive":{"family":"block_cipher","name":"AES","variant":"AES-128","parameters":{}},
            "sampling":{"positive":"cipher","negative":"permutation","independent_units":10,"samples_per_unit":2},
            "features":["xor"],"labels":{"target":"source_distribution"},
            "splits":{"grouping":"key","train":0.7,"validation":0.15,"test":0.15},
            "evaluation":{"metrics":["roc_auc"],"controls":["shuffled_labels"]},
            "provenance":{"implementation_commit":"abc","generator_version":"v1","seed_manifest":"seeds"}
        }
    def test_valid(self):
        self.assertEqual(validate(self.doc), [])
    def test_bad_split(self):
        self.doc["splits"]["test"] = 0.25
        self.assertTrue(validate(self.doc))
    def test_missing_provenance(self):
        self.doc["provenance"].pop("seed_manifest")
        self.assertTrue(validate(self.doc))
    def test_bad_family(self):
        self.doc["primitive"]["family"] = "unknown"
        self.assertTrue(validate(self.doc))
    def test_duplicate_features(self):
        self.doc["features"] = ["xor", "xor"]
        self.assertTrue(validate(self.doc))

if __name__ == "__main__":
    unittest.main()
