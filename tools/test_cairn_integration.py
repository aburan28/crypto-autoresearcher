"""Authority, replay and receipt checks for the Cairn bridge."""
from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairn_publish_objective as publish  # noqa: E402
import cairn_replay_stage1cs as replay  # noqa: E402
import cairn_settlement_receipt as receipt  # noqa: E402
import cairn_autopilot_launchd as launchd  # noqa: E402
import exp_to_objective as e2o  # noqa: E402
from test_exp_to_objective import Repo  # noqa: E402


class BridgeTests(unittest.TestCase):
    def test_the_pinned_replay_matches_an_archived_run_and_refuses_changed_input(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        digest = hashlib.sha256((repo / replay.INPUT).read_bytes()).hexdigest()
        actual = replay.replay(repo, digest)
        archived = e2o.load_manifest(repo, *e2o.STAGE1CS_RUN)[1]["result"]["metrics"]
        self.assertEqual(actual, archived)
        with self.assertRaisesRegex(ValueError, "input hash"):
            replay.replay(repo, "0" * 64)

    def test_publication_is_loopback_only_and_positive_reward_needs_a_decision(self) -> None:
        self.assertEqual(publish.local_node("http://127.0.0.1:8081/"), "http://127.0.0.1:8081")
        for url in ("https://127.0.0.1:8081", "http://example.org:8081", "http://127.0.0.1:8081/a"):
            with self.assertRaises(e2o.BridgeError):
                publish.local_node(url)
        with self.assertRaisesRegex(e2o.BridgeError, "funding-decision"):
            publish.funding(Path("/tmp"), "EXP-X", 1, None, None)

    def test_launchd_carries_trusted_peers_and_validator_identity(self) -> None:
        path = Path("/tmp/cairn")
        config = launchd.render(repo=path, state_dir=path / "state", cairn_bin=path / "bin",
                                identity=path / "worker.json", cairn_data=path / "data",
                                opencode_port=4096, cairn_serve="127.0.0.1:8081",
                                cairn_listen="127.0.0.1:9001", backend="local",
                                opencode_bin=path / "opencode",
                                bootstrap=[path / "peer-a.json", path / "peer-b.json"],
                                attest_identity=path / "validator.json")
        argv = config["ProgramArguments"]
        self.assertEqual(argv.count("--bootstrap"), 2)
        self.assertIn(str(path / "validator.json"), argv)

    def test_receipt_binds_settlement_verdict_and_archived_artifact(self) -> None:
        fixture = Repo()
        self.addCleanup(fixture.cleanup)
        node = "http://127.0.0.1:8081"
        expected = e2o.artifact(fixture.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1")
        objective, _ = e2o.render(fixture.root, "EXP-ECDLP-aaaaaa", "RUN-ECDLP-aaaaaa-1",
                                  "certificate", 0, None, None)
        objective["funder"] = "a" * 64
        objective["funding_signature"] = "b" * 128
        pages = {
            "/objective/sha256:objective": {"id": "sha256:objective",
                                           "settlement": {"claim_id": "sha256:claim", "reward": 0},
                                           "record": objective},
            "/claim/sha256:claim": {"id": "sha256:claim", "record": {
                "objective_id": "sha256:objective", "artifact": expected, "submitter": "alice"}},
            "/knowledge/sha256:claim": {"claim_id": "sha256:claim", "objective_id": "sha256:objective",
                                         "state": {"verdict": "accept", "standing": "accepted"}},
            "/chain": {"ledger_head": "sha256:head", "height": 10},
        }

        def get(url: str, body=None):
            return pages[url.removeprefix(node)]

        with patch.object(receipt, "request_json", side_effect=get), \
                patch.object(receipt, "committed"):
            result = receipt.receipt(fixture.root, node, "EXP-ECDLP-aaaaaa",
                                     "RUN-ECDLP-aaaaaa-1", "sha256:objective", "sha256:claim")
            block = result["external_verification"][0]
            self.assertEqual(block["log_head"], "sha256:head")
            self.assertTrue(block["settled"])
            self.assertEqual(block["approval_decisions"], ["DEC-20260901-aaaaaa"])
            pages["/claim/sha256:claim"]["record"]["artifact"] = {"k": 99}
            with self.assertRaisesRegex(e2o.BridgeError, "artifact differs"):
                receipt.receipt(fixture.root, node, "EXP-ECDLP-aaaaaa",
                                "RUN-ECDLP-aaaaaa-1", "sha256:objective", "sha256:claim")
            pages["/claim/sha256:claim"]["record"]["artifact"] = expected
            pages["/objective/sha256:objective"]["record"]["goal"] = "GOAL-other"
            with self.assertRaisesRegex(e2o.BridgeError, "objective differs"):
                receipt.receipt(fixture.root, node, "EXP-ECDLP-aaaaaa",
                                "RUN-ECDLP-aaaaaa-1", "sha256:objective", "sha256:claim")


if __name__ == "__main__":
    unittest.main()
