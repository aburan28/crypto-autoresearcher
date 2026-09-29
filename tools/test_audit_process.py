"""Infrastructure regressions; no research fixtures or mathematical claims."""
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import audit_process


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "attempt"

    def test_unsupported_native_keeps_terminal_receipt(self):
        with patch.object(audit_process.platform, "system", return_value="Darwin"):
            r = audit_process.run(["never-executed"], self.out, backend="native")
        self.assertEqual(r["status"], "failed_infrastructure")
        self.assertIsNone(r["payload_exit_code"])
        self.assertIsNone(r["cpu_seconds"])
        self.assertEqual(json.loads((self.out / "receipt.json").read_text()), r)
        self.assertTrue((self.out / "launch.json").exists())
        self.assertTrue((self.out / "stderr.log").exists())
        with self.assertRaises(FileExistsError):
            audit_process.run(["never-executed"], self.out)

    def test_worker_limit_failure_never_executes_payload(self):
        with patch.object(audit_process.platform, "system", return_value="Linux"), patch.object(audit_process.resource, "setrlimit", side_effect=ValueError("limit rejected")), patch.object(audit_process.os, "execvp") as execute:
            self.assertEqual(audit_process.worker(1024, 1, ["never-executed"]), 78)
        execute.assert_not_called()

    def test_docker_requires_immutable_image(self):
        with patch.object(audit_process.subprocess, "run") as call:
            r = audit_process.run(["python3"], self.out, backend="docker", image="python:latest")
        call.assert_not_called()
        self.assertEqual(r["status"], "failed_infrastructure")

    def test_docker_limit_mismatch_never_starts_and_cleans(self):
        image = "sha256:" + "a" * 64
        replies = ["linux", json.dumps([{"Id": image, "Os": "linux"}]), "container",
                   json.dumps([{"Id": "container", "HostConfig": {"Memory": 1, "MemorySwap": 1, "NanoCpus": 1}}]), ""]
        calls = []
        def fake(command, **kwargs):
            calls.append(command)
            return subprocess.CompletedProcess(command, 0, replies.pop(0), "")
        with patch.object(audit_process.subprocess, "run", side_effect=fake), patch.object(audit_process.subprocess, "Popen") as start:
            r = audit_process.run(["python3"], self.out, backend="docker", image=image)
        start.assert_not_called()
        self.assertEqual(r["status"], "failed_infrastructure")
        self.assertIn("readback mismatch", r["error"])
        self.assertEqual(calls[-1][1:3], ["rm", "--force"])
        self.assertIn("--memory-swap", calls[2])

    def test_daemon_timeout_is_retained(self):
        with patch.object(audit_process.subprocess, "run", side_effect=subprocess.TimeoutExpired("docker", 1)):
            r = audit_process.run(["python3"], self.out, backend="docker", image="sha256:" + "a" * 64)
        self.assertIn("TimeoutExpired", r["error"])
        self.assertTrue((self.out / "receipt.json").exists())

    @unittest.skipUnless(platform.system() == "Linux", "requires Linux hard memory limits")
    def test_native_success_captures_child_usage(self):
        r = audit_process.run([sys.executable, "-c", "print('payload')"], self.out, seconds=5, memory=256 * 1024**2)
        self.assertEqual(r["status"], "completed")
        self.assertGreater(r["peak_rss_bytes"], 0)
        self.assertGreaterEqual(r["cpu_seconds"], 0)
        self.assertEqual((self.out / "stdout.log").read_text(), "payload\n")

    @unittest.skipUnless(platform.system() == "Linux", "requires Linux hard memory limits")
    def test_native_timeout_retains_receipt(self):
        r = audit_process.run([sys.executable, "-c", "import time; time.sleep(10)"], self.out, seconds=.2)
        self.assertEqual(r["status"], "resource_exhaustion")
        self.assertLess(r["wall_seconds"], 3)

    @unittest.skipUnless(platform.system() == "Linux", "requires Linux hard memory limits")
    def test_native_memory_limit_is_effective(self):
        r = audit_process.run([sys.executable, "-c", "a=bytearray(512*1024**2)"], self.out, seconds=5, memory=128 * 1024**2)
        self.assertEqual(r["status"], "failed_implementation")
        self.assertIn("MemoryError", (self.out / "stderr.log").read_text())


if __name__ == "__main__":
    unittest.main()
