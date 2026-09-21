#!/usr/bin/env python3
"""Tests for tools/cairn_bridge.py.

Split the way the module is: parsing and provisioning logic is mocked and
runs in every environment; `LiveCairnTests` drives a real `cairn-mcp`
binary and is skipped unless `CAIRN_MCP_BIN` already points at one. This
repository's own CI does not build cairn (Stage 0 is opt-in, not a new hard
dependency -- see the module docstring), so the live class is what a
developer with distributed-researcher checked out and built runs locally;
what CI runs on every PR is the mocked half.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairn_bridge as cb


def _completed(*, returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class AvailabilityTests(unittest.TestCase):
    def test_unset_env_and_no_path_binary_is_unavailable(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(cb.ENV_BIN, None)
            with mock.patch("shutil.which", return_value=None):
                self.assertFalse(cb.available())

    def test_configured_binary_must_actually_exist_and_be_executable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "cairn-mcp")
            with mock.patch.dict(os.environ, {cb.ENV_BIN: missing}):
                self.assertFalse(cb.available())

            real = Path(tmp) / "cairn-mcp"
            real.write_text("#!/bin/sh\n")
            real.chmod(0o755)
            with mock.patch.dict(os.environ, {cb.ENV_BIN: str(real)}):
                self.assertTrue(cb.available())

    def test_path_binary_is_used_when_env_is_unset(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(cb.ENV_BIN, None)
            with mock.patch("shutil.which", return_value="/usr/local/bin/cairn-mcp"):
                self.assertTrue(cb.available())


class UnsupportedInputTests(unittest.TestCase):
    def test_unknown_certificate_kind_is_rejected_before_any_subprocess_call(self) -> None:
        with mock.patch("subprocess.run") as run:
            with self.assertRaises(ValueError):
                cb.score_certificate({"kind": "none"})
            run.assert_not_called()

    def test_missing_statement_is_rejected_before_any_subprocess_call(self) -> None:
        with mock.patch.dict(os.environ, {cb.ENV_BIN: "/bin/true"}):
            with mock.patch("subprocess.run") as run:
                with self.assertRaises(ValueError):
                    cb.score_certificate({"kind": "discrete_log"})
                run.assert_not_called()


class ProvisioningTests(unittest.TestCase):
    """`_post_new` / `_ensure_objectives_posted`, subprocess mocked."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log_path = os.path.join(self.tmp.name, "test.jsonl")
        cb._provisioned.clear()

    def test_fresh_post_success_is_trusted_and_cached_to_sidecar(self) -> None:
        full_id = "sha256:" + "a" * 64
        with mock.patch(
            "cairn_bridge._run_cli",
            return_value=_completed(returncode=0, stdout=f"objective {full_id}\n"),
        ):
            ids = cb._post_new("bin", self.log_path, "some/objective.json")
        self.assertEqual(ids, full_id)

    def test_truncated_id_in_a_success_message_is_never_trusted(self) -> None:
        # A real `post` success always prints the full 64-hex digest; this
        # pins that a short token is treated as "no id found", not silently
        # accepted as one -- the bug this design replaced returned exactly
        # this shape of truncated id and it pointed at nothing.
        with mock.patch(
            "cairn_bridge._run_cli",
            return_value=_completed(returncode=0, stdout="objective sha256:822a160c\n"),
        ):
            with self.assertRaises(cb.CairnUnavailableError):
                cb._post_new("bin", self.log_path, "some/objective.json")

    def test_already_posted_with_no_sidecar_is_a_clear_error_not_a_guess(self) -> None:
        with mock.patch(
            "cairn_bridge._run_cli",
            return_value=_completed(
                returncode=2, stderr="refused: objective already posted (sha256:822a160c)\n"
            ),
        ):
            with self.assertRaisesRegex(cb.CairnUnavailableError, "already posted"):
                cb._post_new("bin", self.log_path, "some/objective.json")

    def test_ensure_objectives_posted_reuses_an_existing_sidecar_without_posting(self) -> None:
        known = {"discrete_log": "sha256:" + "b" * 64, "decomposition": "sha256:" + "c" * 64}
        Path(f"{self.log_path}.objective-ids.json").write_text(json.dumps(known))
        with mock.patch("cairn_bridge._post_new") as post_new:
            ids = cb._ensure_objectives_posted("bin", self.log_path)
        post_new.assert_not_called()
        self.assertEqual(ids, known)

    def test_ensure_objectives_posted_is_memoized_per_process(self) -> None:
        known = {"discrete_log": "sha256:" + "b" * 64, "decomposition": "sha256:" + "c" * 64}
        Path(f"{self.log_path}.objective-ids.json").write_text(json.dumps(known))
        first = cb._ensure_objectives_posted("bin", self.log_path)
        # Sidecar gone; a memoized process must not need to re-read it.
        os.remove(f"{self.log_path}.objective-ids.json")
        second = cb._ensure_objectives_posted("bin", self.log_path)
        self.assertEqual(first, second)


class ResponseParsingTests(unittest.TestCase):
    """`score_certificate`'s parse of a real score_candidate response shape."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bin_path = str(Path(self.tmp.name) / "cairn-mcp")
        Path(self.bin_path).write_text("#!/bin/sh\n")
        Path(self.bin_path).chmod(0o755)
        cb._provisioned.clear()
        cb._provisioned[(self.bin_path, cb._log_path(), cb.REPO)] = {
            "discrete_log": "sha256:" + "d" * 64,
            "decomposition": "sha256:" + "e" * 64,
        }

    def _mcp_response(self, text: str) -> subprocess.CompletedProcess:
        payload = {"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": text}]}}
        return _completed(returncode=0, stdout=json.dumps(payload) + "\n")

    def test_accept_with_evidence_parses_status_detail_and_checker_sha(self) -> None:
        text = (
            "accept: verified: 2*P = Q on TOY-P8\n"
            'evidence: {"checker_sha256":"57ae1f13"}\n\n'
            "(Nothing was recorded. This was a local check.)"
        )
        with mock.patch.dict(os.environ, {cb.ENV_BIN: self.bin_path}):
            with mock.patch("subprocess.run", return_value=self._mcp_response(text)):
                verdict = cb.score_certificate(
                    {"kind": "discrete_log", "statement": {"curve": {}, "P": [], "Q": [], "k": 1}}
                )
        self.assertEqual(verdict.status, "accept")
        self.assertEqual(verdict.detail, "verified: 2*P = Q on TOY-P8")
        self.assertEqual(verdict.checker_sha256, "57ae1f13")

    def test_reject_is_returned_normally_not_raised(self) -> None:
        text = 'reject: k*P does not equal Q\nevidence: {"checker_sha256":"57ae1f13"}\n'
        with mock.patch.dict(os.environ, {cb.ENV_BIN: self.bin_path}):
            with mock.patch("subprocess.run", return_value=self._mcp_response(text)):
                verdict = cb.score_certificate(
                    {"kind": "discrete_log", "statement": {"curve": {}, "P": [], "Q": [], "k": 1}}
                )
        self.assertEqual(verdict.status, "reject")

    def test_unavailable_from_cairn_is_a_normal_return_not_an_exception(self) -> None:
        # docs/cairn-integration-plan.md invariant (b): unavailable is never
        # a rejection, and it is also never this bridge's own error -- it is
        # cairn answering, just not with a verdict on the artifact.
        text = "unavailable: 'lean' not on PATH; install a Lean toolchain to verify\n"
        with mock.patch.dict(os.environ, {cb.ENV_BIN: self.bin_path}):
            with mock.patch("subprocess.run", return_value=self._mcp_response(text)):
                verdict = cb.score_certificate(
                    {"kind": "discrete_log", "statement": {"curve": {}, "P": [], "Q": [], "k": 1}}
                )
        self.assertEqual(verdict.status, "unavailable")

    def test_unparseable_response_raises_cairn_unavailable_not_a_bare_exception(self) -> None:
        with mock.patch.dict(os.environ, {cb.ENV_BIN: self.bin_path}):
            with mock.patch(
                "subprocess.run",
                return_value=_completed(returncode=1, stdout="", stderr="segfault"),
            ):
                with self.assertRaises(cb.CairnUnavailableError):
                    cb.score_certificate(
                        {"kind": "discrete_log", "statement": {"curve": {}, "P": [], "Q": [], "k": 1}}
                    )

    def test_timeout_raises_cairn_unavailable(self) -> None:
        with mock.patch.dict(os.environ, {cb.ENV_BIN: self.bin_path}):
            with mock.patch(
                "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="cairn-mcp", timeout=30)
            ):
                with self.assertRaises(cb.CairnUnavailableError):
                    cb.score_certificate(
                        {"kind": "discrete_log", "statement": {"curve": {}, "P": [], "Q": [], "k": 1}}
                    )


@unittest.skipUnless(cb.available(), f"set {cb.ENV_BIN} to a built cairn-mcp to run live tests")
class LiveCairnTests(unittest.TestCase):
    """Drives a real cairn-mcp process. Skipped when none is configured."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log_patch = mock.patch.dict(
            os.environ, {cb.ENV_LOG: os.path.join(self.tmp.name, "live.jsonl")}
        )
        self.log_patch.start()
        self.addCleanup(self.log_patch.stop)
        cb._provisioned.clear()

    def test_real_discrete_log_certificate_round_trips(self) -> None:
        verdict = cb.score_certificate({
            "kind": "discrete_log",
            "statement": {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42], "Q": [81, 42], "k": 2},
        })
        self.assertEqual(verdict.status, "accept")

        corrupted = cb.score_certificate({
            "kind": "discrete_log",
            "statement": {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42], "Q": [81, 42], "k": 3},
        })
        self.assertEqual(corrupted.status, "reject")

    def test_real_decomposition_certificate_round_trips(self) -> None:
        verdict = cb.score_certificate({
            "kind": "decomposition",
            "statement": {
                "curve": {"p": 2293, "a": 0, "b": 417},
                "target": [1534, 1689],
                "summands": [[1023, 84], [1583, 354], [877, 988]],
            },
        })
        self.assertEqual(verdict.status, "accept")

    def test_nothing_is_recorded_beyond_the_two_provisioned_objectives(self) -> None:
        cb.score_certificate({
            "kind": "discrete_log",
            "statement": {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42], "Q": [81, 42], "k": 2},
        })
        cb.score_certificate({
            "kind": "discrete_log",
            "statement": {"curve": {"p": 223, "a": 0, "b": 171}, "P": [105, 42], "Q": [81, 42], "k": 999},
        })
        with open(cb._log_path(), encoding="utf-8") as fh:
            entries = [json.loads(line) for line in fh if line.strip()]
        self.assertEqual(len(entries), 2)
        self.assertTrue(all(e["kind"] == "objective" for e in entries))


if __name__ == "__main__":
    unittest.main()
