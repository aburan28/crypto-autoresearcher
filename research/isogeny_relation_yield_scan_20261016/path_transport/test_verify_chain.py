"""Integrity checks for the independent checkpoint verifier."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from verify_chain import point_hash, verify

HERE = Path(__file__).resolve().parent
CONTROLS = HERE / "controls"
PRIOR = HERE.parent / "preparation" / "controls" / "attempt-3" / "result.json"


class CheckpointVerifierTests(unittest.TestCase):
    def test_fixed_first_check_vertices(self):
        for stratum, edges, points in (("P29", 8, 4096), ("P37", 4, 12800)):
            with self.subTest(stratum=stratum):
                result = verify(stratum, CONTROLS / f"{stratum.lower()}-twoedge-attempt1")
                self.assertEqual(result["status"], "pass")
                self.assertEqual(result["edges_checked"], edges)
                self.assertEqual(result["points_replayed"], points)

    def test_prior_pointwise_digests(self):
        prior = {row["stratum"]: row for row in json.loads(PRIOR.read_text())["results"]}
        for stratum in ("P29", "P37"):
            directory = CONTROLS / f"{stratum.lower()}-twoedge-attempt1"
            with self.subTest(stratum=stratum):
                for edge in prior[stratum]["edges"]:
                    record = json.loads((directory / f"edge-{edge['index']:04d}.json").read_text())
                    self.assertEqual(record["base_sha256"], edge["base_sha256"])

    def test_self_consistent_terminal_point_tamper_is_rejected(self):
        source = CONTROLS / "p29-twoedge-attempt1"
        with tempfile.TemporaryDirectory(prefix="isogeny-chain-tamper-") as temporary:
            directory = Path(temporary) / "chain"
            shutil.copytree(source, directory)
            path = directory / "edge-0008.json"
            record = json.loads(path.read_text())
            record["base"][0][1] = (record["base"][0][1] + 1) % 320092037
            record["base_sha256"] = point_hash(record["base"])
            path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            with self.assertRaisesRegex(ValueError, "independent full-base map replay differs"):
                verify("P29", directory)


if __name__ == "__main__":
    unittest.main()
