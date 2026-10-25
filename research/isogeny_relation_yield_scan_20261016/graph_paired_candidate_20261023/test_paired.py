"""Controls for paired targetwise occupancy summaries."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name("paired.py")
spec = importlib.util.spec_from_file_location("graph_paired", MODULE)
assert spec and spec.loader
paired = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paired)


class PairedControls(unittest.TestCase):
    def test_checked_p37_bounded_fixture(self):
        study = MODULE.parents[1]
        folder = study / "graph_solve_candidate_20261023/controls/attempt-3"
        path = folder / "collector.stdout"
        checked = json.loads((folder / "rank_verify.stdout").read_text())
        target_lines = [line.split("\t") for line in path.read_text().splitlines()
                        if line.startswith("target\t")]
        coefficient_sha = hashlib.sha256("".join(
            f"{fields[2]},{fields[3]}\n" for fields in target_lines).encode()).hexdigest()
        expected = {"p": 81640512137, "r": 81640511861,
                    "base_x_orbits": 1600, "target_count": 8}
        indicators = paired.occupancy(path, expected, coefficient_sha, paired.sha(path))
        self.assertEqual(sum(indicators), checked["useful_targets"])

    def test_counts(self):
        result = paired.paired_counts([True, True, False, False],
                                      [True, False, True, False])
        self.assertEqual((result["both"], result["left_only"],
                          result["right_only"], result["neither"]), (1, 1, 1, 1))
        self.assertEqual(result["paired_difference"], {"numerator": 0, "denominator": 4})

    def test_collector_binding_and_mutation_refusal(self):
        data = ("collector-v1\t19\t19\t4\t3\n"
                "target\t0\t1\t2\t0\t0\t0\n"
                "target\t1\t3\t4\t1\t6\t1\n"
                "triple\t1\t0\t1\t2\n"
                "target\t2\t5\t6\t0\t0\t0\n")
        expected = {"p": 19, "r": 19, "base_x_orbits": 2, "target_count": 3}
        coefficient_sha = hashlib.sha256(b"1,2\n3,4\n5,6\n").hexdigest()
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "collector.stdout"
            path.write_text(data)
            digest = paired.sha(path)
            self.assertEqual(paired.occupancy(path, expected, coefficient_sha, digest),
                             [False, True, False])
            with self.assertRaisesRegex(ValueError, "digest differs"):
                paired.occupancy(path, expected, coefficient_sha, "0" * 64)
            with self.assertRaisesRegex(ValueError, "paired coefficients differ"):
                paired.occupancy(path, expected, "0" * 64, digest)
            path.write_text(data.replace("target\t1", "target\t2"))
            with self.assertRaisesRegex(ValueError, "target order differs"):
                paired.occupancy(path, expected, coefficient_sha, paired.sha(path))


if __name__ == "__main__":
    unittest.main()
