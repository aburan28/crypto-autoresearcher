from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import verify_exact_merge_certificate as verifier


def blob_oid(data: bytes) -> str:
    framed = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(framed).hexdigest()


class Fixture:
    def __init__(self, root: Path, *, extra_conflict: bool = False,
                 candidate_data: bytes = b"resolved goal\n"):
        self.root = root
        self.repo = root / "repo"
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env.update({
            "GIT_AUTHOR_NAME": "Certificate Test",
            "GIT_AUTHOR_EMAIL": "certificate@example.test",
            "GIT_COMMITTER_NAME": "Certificate Test",
            "GIT_COMMITTER_EMAIL": "certificate@example.test",
            "GIT_CONFIG_NOSYSTEM": "1",
        })
        self.git("init", "-b", "main")
        self.write("shared.txt", b"shared\n")
        self.write("goal.txt", b"base goal\n")
        self.git("add", "shared.txt", "goal.txt")
        self.git("commit", "-m", "base")
        self.base = self.rev("HEAD")

        self.git("checkout", "-b", "second", self.base)
        self.write("goal.txt", b"second goal\n")
        for index in range(6):
            self.write(f"conflicts/c{index}.txt", f"second-{index}\n".encode())
        if extra_conflict:
            self.write("conflicts/extra.txt", b"second-extra\n")
        self.git("add", "goal.txt", "conflicts")
        self.git("commit", "-m", "second")
        self.second = self.rev("HEAD")

        self.git("checkout", "-b", "first", self.base)
        self.write("goal.txt", b"first goal\n")
        for index in range(6):
            self.write(f"conflicts/c{index}.txt", f"first-{index}\n".encode())
        if extra_conflict:
            self.write("conflicts/extra.txt", b"first-extra\n")
        self.git("add", "goal.txt", "conflicts")
        self.git("commit", "-m", "repair authoring base")
        self.repair_base = self.rev("HEAD")

        self.candidate_rel = "contract/candidate.blob"
        self.manifest_rel = "contract/manifest.yaml"
        self.write(self.candidate_rel, candidate_data)
        candidate_hash = hashlib.sha256(candidate_data).hexdigest()
        candidate_oid = blob_oid(candidate_data)
        resolutions = []
        for index in range(6):
            path = f"conflicts/c{index}.txt"
            resolutions.append({
                "index": index + 1,
                "path": path,
                "mode": "100644",
                "selection": "frozen_origin_main_body_for_namespace_serialization_only",
                "source_commit": self.second,
                "source_git_blob_oid_sha1": self.rev(f"{self.second}:{path}"),
                "source_sha256": "0" * 64,
                "size_bytes": len(f"second-{index}\n"),
            })
        resolutions.append({
            "index": 7,
            "path": "goal.txt",
            "mode": "100644",
            "selection": "pre_reviewed_neutral_third_body",
            "source_path": self.candidate_rel,
            "source_git_blob_oid_sha1": candidate_oid,
            "source_sha256": candidate_hash,
            "size_bytes": len(candidate_data),
        })
        manifest = {
            "merge_resolution_manifest": {
                "schema": verifier.MANIFEST_SCHEMA,
                "correction_id": "CORR-TEST-abcdef",
                "task_id": "TASK-TEST-abcdef",
                "goal_id": "GOAL-TEST-001",
                "frozen_source_projection": {
                    "merge_base": self.base,
                    "repair_authoring_base": self.repair_base,
                    "required_second_parent": self.second,
                },
                "conflict_summary": {
                    "exact_conflict_count": 7,
                    "immutable_add_add_count": 6,
                    "mutable_goal_projection_count": 1,
                },
                "canonical_resolutions": resolutions,
            }
        }
        manifest_data = yaml.safe_dump(manifest, sort_keys=False).encode()
        self.write(self.manifest_rel, manifest_data)
        self.git("add", self.candidate_rel, self.manifest_rel)
        self.git("commit", "-m", "frozen contract")
        self.first = self.rev("HEAD")
        self.manifest_sha256 = hashlib.sha256(manifest_data).hexdigest()
        self.allowed_paths = [self.candidate_rel, self.manifest_rel]
        self.canonical_paths = [f"conflicts/c{i}.txt" for i in range(6)] + ["goal.txt"]
        self.candidate_data = candidate_data

    def git(self, *args: str, check: bool = True,
            input_data: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
        proc = subprocess.run(
            ["git", *args], cwd=self.repo, env=self.env, input=input_data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if check and proc.returncode != 0:
            self.fail_command(args, proc)
        return proc

    def fail_command(self, args: tuple[str, ...], proc: subprocess.CompletedProcess[bytes]) -> None:
        raise AssertionError(
            f"git {' '.join(args)} failed {proc.returncode}: "
            f"{proc.stderr.decode(errors='replace')}")

    def rev(self, ref: str) -> str:
        return self.git("rev-parse", ref).stdout.decode().strip()

    def write(self, relative: str, data: bytes) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    @property
    def manifest(self) -> Path:
        return self.repo / self.manifest_rel

    @property
    def candidate(self) -> Path:
        return self.repo / self.candidate_rel

    def verify_pre(self, *, first: str | None = None,
                   second: str | None = None,
                   allowed: list[str] | None = None) -> dict:
        return verifier.verify_pre(
            self.repo, self.manifest, self.candidate, self.manifest_sha256,
            first or self.first, second or self.second,
            self.allowed_paths if allowed is None else allowed)

    def create_merge(self, *, goal_data: bytes | None = None) -> str:
        self.git("checkout", "first")
        proc = self.git("merge", "--no-ff", "--no-commit", self.second, check=False)
        if proc.returncode == 0:
            raise AssertionError("fixture unexpectedly merged without conflicts")
        for index in range(6):
            path = f"conflicts/c{index}.txt"
            data = self.git("show", f"{self.second}:{path}").stdout
            self.write(path, data)
        self.write("goal.txt", self.candidate_data if goal_data is None else goal_data)
        self.git("add", *self.canonical_paths)
        self.git("commit", "-m", "exact merge")
        return self.rev("HEAD")

    def ledger_result(self, merge: str, *, exit_code: int = 0,
                      new_violations: int = 0) -> Path:
        path = self.root / "ledger-result.json"
        path.write_text(json.dumps({
            "schema": verifier.LEDGER_RESULT_SCHEMA,
            "merge_commit": merge,
            "command": ["python3", "tools/validate_ledger.py"],
            "exit_code": exit_code,
            "new_violations": new_violations,
        }), encoding="utf-8")
        return path

    def verify_post(self, merge: str, ledger: Path | None = None) -> dict:
        return verifier.verify_post(
            self.repo, self.manifest, self.candidate, self.manifest_sha256,
            self.first, self.second, merge, self.allowed_paths,
            ledger_validation_result=ledger or self.ledger_result(merge))


class ExactMergeCertificateTests(unittest.TestCase):
    def make_fixture(self, **kwargs) -> tuple[tempfile.TemporaryDirectory, Fixture]:
        temporary = tempfile.TemporaryDirectory()
        return temporary, Fixture(Path(temporary.name), **kwargs)

    def test_pre_happy_path_checks_exact_seven_conflicts(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        result = fixture.verify_pre()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(result["conflicts"]), 7)
        self.assertEqual(
            [item["class"] for item in result["conflicts"]].count("add/add"), 6)
        self.assertEqual(
            [item["class"] for item in result["conflicts"]].count("content"), 1)
        self.assertEqual(result["experiment_runs"], 0)

    def test_cli_pre_happy_path(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        command = [
            sys.executable, str(REPO / "tools" / "verify_exact_merge_certificate.py"),
            "pre", "--repository", str(fixture.repo),
            "--manifest", str(fixture.manifest),
            "--candidate", str(fixture.candidate),
            "--expected-manifest-sha256", fixture.manifest_sha256,
            "--expected-first-parent", fixture.first,
            "--expected-second-parent", fixture.second,
        ]
        for path in fixture.allowed_paths:
            command.extend(["--first-parent-path", path])
        proc = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        self.assertEqual(json.loads(proc.stdout)["status"], "PASS")

    def test_rejects_disjoint_first_parent_path_change(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        fixture.write("unrelated.txt", b"disjoint drift\n")
        fixture.git("add", "unrelated.txt")
        fixture.git("commit", "-m", "disjoint drift")
        drifted = fixture.rev("HEAD")
        with self.assertRaisesRegex(verifier.VerificationError, "unexpected=.*unrelated.txt"):
            fixture.verify_pre(first=drifted)

    def test_seven_oid_only_false_assurance_is_rejected(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        fixture.write("notes/attacker.txt", b"not covered by seven OIDs\n")
        fixture.git("add", "notes/attacker.txt")
        fixture.git("commit", "-m", "seven-oids-only counterexample")
        drifted = fixture.rev("HEAD")
        for path in fixture.canonical_paths:
            self.assertEqual(
                fixture.rev(f"{fixture.repair_base}:{path}"),
                fixture.rev(f"{drifted}:{path}"),
                path,
            )
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "complete first-parent changed-path allowlist mismatch"):
            fixture.verify_pre(first=drifted)

    def test_rejects_extra_conflict(self):
        temporary, fixture = self.make_fixture(extra_conflict=True)
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "predicted conflict set/classes mismatch"):
            fixture.verify_pre()

    def test_rejects_alternate_second_parent(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "manifest second parent differs"):
            fixture.verify_pre(second=fixture.base)

    def test_rejects_candidate_mismatch(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        fixture.candidate.write_bytes(b"substituted candidate\n")
        with self.assertRaisesRegex(verifier.VerificationError, "candidate (SHA-256|byte size)"):
            fixture.verify_pre()

    def test_rejects_dirty_premerge_repository(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        fixture.write("untracked.txt", b"dirty\n")
        with self.assertRaisesRegex(verifier.VerificationError, "dirty"):
            fixture.verify_pre()

    def test_rejects_duplicate_key_manifest(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        data = fixture.manifest.read_bytes() + b"merge_resolution_manifest: {}\n"
        fixture.manifest.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        with self.assertRaisesRegex(verifier.VerificationError, "duplicate YAML key"):
            verifier.verify_pre(
                fixture.repo, fixture.manifest, fixture.candidate, digest,
                fixture.first, fixture.second, fixture.allowed_paths)

    def test_post_happy_path_reconstructs_complete_tree(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        merge = fixture.create_merge()
        result = fixture.verify_post(merge)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["ordered_parents"], [fixture.first, fixture.second])
        self.assertTrue(result["candidate_bytes_equal"])
        self.assertEqual(result["ledger_validation"]["new_violations"], 0)
        self.assertEqual(result["experiment_runs"], 0)

    def test_post_rejects_swapped_parent_order(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        merge = fixture.create_merge()
        tree = fixture.rev(f"{merge}^{{tree}}")
        swapped = fixture.git(
            "commit-tree", tree, "-p", fixture.second, "-p", fixture.first,
            input_data=b"swapped parents\n").stdout.decode().strip()
        fixture.git("checkout", "--detach", swapped)
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "exactly two ordered parents"):
            fixture.verify_post(swapped)

    def test_post_rejects_extra_parent(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        merge = fixture.create_merge()
        tree = fixture.rev(f"{merge}^{{tree}}")
        octopus = fixture.git(
            "commit-tree", tree, "-p", fixture.first, "-p", fixture.second,
            "-p", fixture.base, input_data=b"extra parent\n").stdout.decode().strip()
        fixture.git("checkout", "--detach", octopus)
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "exactly two ordered parents"):
            fixture.verify_post(octopus)

    def test_post_rejects_wrong_merge_tree_and_candidate(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        merge = fixture.create_merge(goal_data=b"wrong goal\n")
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "merge tree differs"):
            fixture.verify_post(merge)

    def test_post_rejects_failed_ledger_result(self):
        temporary, fixture = self.make_fixture()
        self.addCleanup(temporary.cleanup)
        merge = fixture.create_merge()
        failed = fixture.ledger_result(merge, exit_code=1, new_violations=1)
        with self.assertRaisesRegex(verifier.VerificationError,
                                    "not a zero-new-violation success"):
            fixture.verify_post(merge, failed)

    def test_post_rejects_conflict_markers_even_when_candidate_is_reviewed(self):
        marker_candidate = b"<<<<<<< ours\nvalue\n>>>>>>> theirs\n"
        temporary, fixture = self.make_fixture(candidate_data=marker_candidate)
        self.addCleanup(temporary.cleanup)
        merge = fixture.create_merge()
        with self.assertRaisesRegex(verifier.VerificationError, "conflict marker"):
            fixture.verify_post(merge)


if __name__ == "__main__":
    unittest.main()
