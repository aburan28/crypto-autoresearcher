"""tools/cairn_seam_demo.py: the seam, driven end to end.

The walk itself needs a cairn binary built with the reader, so the one test
that runs it is gated on CAIRN_BIN and skips with a reason otherwise; CI
without cairn still holds the parts that do not need one -- what the script
refuses, and how it reads the node's answers -- so a change to cairn's output
shapes fails here before it fails an operator.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairn_seam_demo as demo  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def fake_binary(directory: Path, banner: str) -> Path:
    path = directory / "cairn"
    path.write_text(f"#!/bin/sh\nprintf '%s\\n' \"{banner}\"\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class RefusalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_no_binary_is_unusable_not_a_traceback(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "CAIRN_BIN"}
        env["PATH"] = str(self.dir)
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(demo.Unusable) as caught:
                demo.find_cairn(None)
        self.assertIn("no cairn binary", str(caught.exception))

    def test_a_binary_without_the_reader_is_named_as_the_reason(self) -> None:
        plain = fake_binary(self.dir, "cairn 1.15.3")
        with self.assertRaises(demo.Unusable) as caught:
            demo.find_cairn(str(plain))
        self.assertIn("without the reader", str(caught.exception))
        self.assertIn("cairn 1.15.3", str(caught.exception))

    def test_a_binary_with_the_reader_is_accepted(self) -> None:
        full = fake_binary(self.dir, "cairn 1.15.3\n  ui       embedded -- cairn run will start")
        self.assertEqual(demo.find_cairn(str(full)), str(full))

    def test_main_exits_3_when_cairn_is_unusable(self) -> None:
        plain = fake_binary(self.dir, "cairn 0.0.0")
        self.assertEqual(demo.main(["--cairn", str(plain), "--work", str(self.dir / "w")]), 3)


class ParsingTests(unittest.TestCase):
    """The shapes the script reads out of cairn's text answers."""

    def test_ids_and_verdicts_are_read_from_the_lines_cairn_prints(self) -> None:
        claim = "sha256:" + "a" * 64
        reveal = (f"claim {claim}\ntrusted citation: {{\"claim_id\":\"{claim}\",\"capability\":\"x\"}}\n"
                  f"verdict: accept: verified: 11*P = Q on TOY-P16\nsettled: false\nreward: 0\n")
        self.assertEqual(demo.CLAIM_ID.search(reveal).group(1), claim)
        self.assertEqual(demo.VERDICT.search(reveal).group(1), "accept")
        self.assertEqual(demo.SCORE.search("accept: verified: 11*P = Q\n").group(1), "accept")
        self.assertEqual(demo.SCORE.search("reject: k*P != Q\n").group(1), "reject")
        objective = "sha256:" + "b" * 64
        self.assertEqual(demo.OBJECTIVE_ID.search(f"objective {objective}\n  reward 1\n").group(1), objective)
        self.assertIsNone(demo.VERDICT.search("verdict: maybe\n"))

    def test_mcp_answers_are_matched_by_id_and_errors_are_refusals(self) -> None:
        # A stand-in server that answers every call in reverse order, so
        # matching by id rather than by arrival is what the test holds.
        script = (
            "import json, sys\n"
            "lines = [json.loads(l) for l in sys.stdin]\n"
            "for doc in reversed(lines):\n"
            "    if doc['params']['name'] == 'boom':\n"
            "        out = {'jsonrpc': '2.0', 'id': doc['id'], 'error': {'message': 'no such tool'}}\n"
            "    else:\n"
            "        out = {'jsonrpc': '2.0', 'id': doc['id'], 'result': {'content': [{'type': 'text',"
            " 'text': 'answer ' + str(doc['id'])}]}}\n"
            "    print(json.dumps(out), flush=True)\n"
        )
        process = subprocess.Popen(  # noqa: S603
            [sys.executable, "-c", script], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
        )
        mcp = demo.Mcp(process)
        ids = [mcp.send("tools/call", {"name": name, "arguments": {}}) for name in ("one", "boom", "two")]
        assert process.stdin is not None
        process.stdin.close()  # the stand-in answers everything at EOF, last first
        self.assertEqual(mcp.receive(ids[0], timeout=10)["result"]["content"][0]["text"], f"answer {ids[0]}")
        self.assertEqual(mcp.receive(ids[2], timeout=10)["result"]["content"][0]["text"], f"answer {ids[2]}")
        self.assertIn("error", mcp.receive(ids[1], timeout=10))
        with self.assertRaises(demo.Refused) as caught:
            mcp.receive(99, "never-sent", timeout=0.3)
        self.assertIn("never-sent", str(caught.exception))
        process.wait(timeout=10)


@unittest.skipUnless(os.environ.get("CAIRN_BIN"), "set CAIRN_BIN to a cairn built with the reader to run the walk")
class EndToEndTests(unittest.TestCase):
    def test_a_committed_run_goes_through_the_seam_and_the_receipt_is_clean(self) -> None:
        cairn = os.environ["CAIRN_BIN"]
        banner = subprocess.run([cairn, "--version"], capture_output=True, text=True, check=False)
        if "embedded" not in banner.stdout + banner.stderr:
            self.skipTest(f"{cairn} was built without the reader; `cairn run` needs it")
        work = Path(tempfile.mkdtemp(prefix="seam-test-"))
        self.addCleanup(shutil.rmtree, work, True)
        code = demo.main([
            "--cairn", cairn, "--work", str(work),
            "--serve", f"127.0.0.1:{free_port()}", "--listen", f"127.0.0.1:{free_port()}",
        ])
        self.assertEqual(code, 0)
        receipt = (work / "external_verification.yaml").read_text(encoding="utf-8")
        self.assertIn("verdict: accept", receipt)
        self.assertIn("settled: true", receipt)
        self.assertIn("witness: RUN-DTREE-010 raw-result.json.certificates[0]", receipt)
        self.assertTrue((work / "cairn.jsonl").is_file())


if __name__ == "__main__":
    unittest.main()
