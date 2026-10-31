"""Checkpoint portability regressions; isolated Git fixtures, no network."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/checkpoint.sh"


class CheckpointStatTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="checkpoint-stat-test-")
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.tmp = self.base / "tmp"
        self.tmp.mkdir()
        # Never inherit a credential or call a real uploader in these fixtures.
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("AWS_", "CHECKPOINT_"))}
        self.env.update(PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        TMPDIR=str(self.tmp),
                        CHECKPOINT_TOKEN_FILE=str(self.base / "absent-token"),
                        CHECKPOINT_AWS_PROFILE="checkpoint-test-absent-profile")
        self.stub("aws", "#!/bin/sh\nexit 1\n")
        self.stub("curl", "#!/bin/sh\necho 'unexpected network call' >&2\nexit 97\n")
        shutil.copy2(SCRIPT, self.repo / "checkpoint.sh")
        self.git("init", "-q")
        self.git("add", "checkpoint.sh")
        self.git("-c", "user.name=Checkpoint Fixture",
                 "-c", "user.email=checkpoint-fixture@example.invalid",
                 "-c", "commit.gpgSign=false", "commit", "-qm", "fixture")
        resume = self.repo / ".resume"
        resume.mkdir()
        sections = ["Goal", "Lead / hypothesis", "Spec", "State", "Next steps",
                    "Runs in flight", "Stop and success conditions"]
        (resume / "RESUME.md").write_text("\n".join(
            f"## {section}\nIsolated software fixture; no experiment.\n"
            for section in sections))
        # Exercise untracked-file hashing and packaging, including a spaced name.
        (self.repo / "untracked payload.txt").write_bytes(b"fixture payload\n")

    def stub(self, name, source):
        path = self.bin / name
        path.write_text(source)
        path.chmod(0o755)

    def stub_python_metadata_failure(self):
        real_python = shutil.which("python3")
        self.assertIsNotNone(real_python)
        self.stub("python3", f"""#!/bin/sh
if [ "$1" = "-" ] && [ "$2" = "untracked payload.txt" ]; then
  echo failed-stat-output
  exit 1
fi
exec {real_python} "$@"
""")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                              check=True, capture_output=True, text=True)

    def gate(self):
        return subprocess.run(["bash", "checkpoint.sh", "gate"], cwd=self.repo,
                              env=self.env, capture_output=True, text=True,
                              timeout=20)

    def assert_auth_refusal(self, result):
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no way to upload", result.stderr)
        self.assertIn("nothing was checkpointed", result.stderr)
        self.assertNotIn("integer expression expected", result.stderr)
        self.assertNotIn("unbound variable", result.stderr)
        self.assertNotIn("unexpected network call", result.stderr)
        self.assertNotIn("failed-stat-output", result.stdout + result.stderr)
        self.assertFalse((self.repo / ".resume/.last-push").exists())

    def test_native_python_metadata_reaches_auth_refusal_with_untracked_files(self):
        self.assert_auth_refusal(self.gate())

    def test_metadata_does_not_depend_on_stat_command(self):
        # A noisy external stat shim must not contaminate metadata or the receipt.
        self.stub("stat", """#!/usr/bin/env python3
import os, sys
if sys.argv[1] != '-f':
    print('failed-stat-output')
    sys.exit(1)
name = sys.argv[3]
s = os.stat(name)
if sys.argv[2] == '%z':
    print(s.st_size)
elif sys.argv[2] == '%N %z %m':
    print(name, s.st_size, int(s.st_mtime))
else:
    sys.exit(2)
""")
        self.assert_auth_refusal(self.gate())

    def test_failed_metadata_read_refuses_without_accepting_partial_output(self):
        self.stub_python_metadata_failure()
        result = self.gate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot hash the current worktree", result.stderr)
        self.assertNotIn("failed-stat-output", result.stdout + result.stderr)
        self.assertNotIn("unexpected network call", result.stderr)
        self.assertFalse((self.repo / ".resume/.last-push").exists())

    def test_failed_stat_cannot_reuse_receipt_for_state_without_new_file(self):
        payload = self.repo / "untracked payload.txt"
        payload.unlink()
        definitions = self.base / "state-hash-fixture.sh"
        definitions.write_text((self.repo / "checkpoint.sh").read_text().split(
            'case "${1:-}" in', 1)[0] + "\nstate_hash\n")
        baseline = subprocess.run(["bash", str(definitions)], cwd=self.repo,
                                  env=self.env, check=True, capture_output=True,
                                  text=True, timeout=20).stdout.strip()
        self.assertRegex(baseline, r"^[0-9a-f]{64}$")
        # A synthetic prior receipt in an isolated fixture is never a real gate.
        prior = baseline + " fixture-stamp s3://fixture-not-an-upload/\n"
        receipt = self.repo / ".resume/.last-push"
        receipt.write_text(prior)
        payload.write_bytes(b"new payload\n")
        self.stub_python_metadata_failure()
        for command in ("gate", "status"):
            with self.subTest(command=command):
                result = subprocess.run(["bash", "checkpoint.sh", command],
                                        cwd=self.repo, env=self.env,
                                        capture_output=True, text=True, timeout=20)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("cannot hash the current worktree", result.stderr)
                self.assertNotIn("unchanged since", result.stdout)
                self.assertNotIn("unexpected network call", result.stderr)
                self.assertNotIn("failed-stat-output", result.stdout + result.stderr)
                self.assertEqual(receipt.read_text(), prior)

    def test_size_limit_still_excludes_nonempty_untracked_payload(self):
        self.env["CHECKPOINT_MAX_FILE_MB"] = "0"
        self.assert_auth_refusal(self.gate())
        skipped = list(self.tmp.glob("checkpoint.*/skipped-untracked.txt"))
        self.assertEqual(len(skipped), 1)
        self.assertIn("untracked payload.txt\t16 bytes", skipped[0].read_text())


if __name__ == "__main__":
    unittest.main()
