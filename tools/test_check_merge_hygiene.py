#!/usr/bin/env python3
"""Tests for the merge-hygiene gate.

Every test here replays a defect that actually reached main in the PR #55/#58
window. If one regresses, this tool is decorative:

  - `test_catches_the_markers_that_shipped` — nine files, including two
    coordinator decisions and the technique abstract `CLAUDE.md` names, were
    merged holding literal `<<<<<<< HEAD` lines. Nothing looked for them.
  - `test_catches_a_record_this_branch_broke` — a record that does not parse
    cannot be schema-checked, so breaking one REMOVES validator errors. Under
    a relative gate that reads as an improvement.
  - `test_baseline_does_not_excuse_a_newly_broken_record` — the baseline exists
    only so the gate could be switched on over a corpus with 19 pre-existing
    failures. It must never absorb a new one.
  - `test_catches_the_id_allocated_twice` — `DEC-20260728-004` was spent on two
    unrelated decisions by two branches, each of which had correctly grepped
    its own tree. Only a comparison against the remote can see it.
  - `test_setext_heading_is_not_a_conflict_marker` — a bare `=======` rule is
    legal Markdown and appears throughout `knowledge/`. Matching it would make
    the gate fire on the corpus it protects.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_merge_hygiene as mh


def git(cwd, *args):
    return subprocess.run(("git",) + args, cwd=cwd, capture_output=True,
                          text=True, check=True)


class _Repo:
    """A throwaway git repo with `mh` pointed at it."""

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = self.tmp.name
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "user.email", "t@example.com")
        git(self.path, "config", "user.name", "t")
        self._saved = mh.REPO
        mh.REPO = self.path
        return self

    def __exit__(self, *exc):
        mh.REPO = self._saved
        self.tmp.cleanup()

    def write(self, rel, text):
        full = os.path.join(self.path, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)

    def commit(self, msg="c"):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", msg)


# The exact shape that shipped: a record whose two sides were left in place.
#
# Assembled from pieces rather than written literally, because a test file
# containing a real marker at the start of a line would be caught by the very
# gate it tests -- and the honest fix is to not put one there, not to carve an
# exception into the gate. (The first draft of this file did exactly that, and
# the gate rejected it.)
_OPEN = "<" * 7
_MID = "=" * 7
_CLOSE = ">" * 7

CONFLICTED = (
    "coordinator_decision:\n"
    "  id: DEC-20260728-004\n"
    f"{_OPEN} HEAD\n"
    "  decision: revise\n"
    f"{_MID}\n"
    "  decision: support\n"
    f"{_CLOSE} origin/main\n"
)


class MarkerTests(unittest.TestCase):
    def test_catches_the_markers_that_shipped(self) -> None:
        with _Repo() as r:
            r.write("ledger/decisions/DEC-20260728-004.yaml", CONFLICTED)
            r.commit()
            bad = mh.check_markers(mh.tracked_files())
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("unresolved conflict marker", bad[0])

    def test_setext_heading_is_not_a_conflict_marker(self) -> None:
        with _Repo() as r:
            r.write("knowledge/techniques/KN-TECH-056.md",
                    "Heading\n=======\n\nbody\n")
            r.commit()
            self.assertEqual(mh.check_markers(mh.tracked_files()), [])

    def test_clean_tree_passes(self) -> None:
        with _Repo() as r:
            r.write("ledger/decisions/DEC-1.yaml", "coordinator_decision:\n  id: x\n")
            r.commit()
            self.assertEqual(mh.check_markers(mh.tracked_files()), [])


class ParseTests(unittest.TestCase):
    def test_catches_a_record_this_branch_broke(self) -> None:
        with _Repo() as r:
            # Unquoted ": " inside a plain scalar — the defect that made
            # DEC-20260727-010 unreadable.
            r.write("ledger/decisions/DEC-20260727-010.yaml",
                    "coordinator_decision:\n"
                    "  scope:\n"
                    "    added: 4 (two per file); removed: 0\n")
            r.commit()
            bad = mh.check_parses(mh.tracked_files())
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("does not parse", bad[0])

    def test_baseline_does_not_excuse_a_newly_broken_record(self) -> None:
        with _Repo() as r:
            r.write("ledger/a.yaml", "x: [unterminated\n")
            r.write("ledger/b.yaml", "y: [also broken\n")
            # Only the first is grandfathered.
            r.write("tools/merge_hygiene_baseline.txt",
                    mh.BASELINE_HEADER + "ledger/a.yaml\n")
            r.commit()
            mh.BASELINE = os.path.join(r.path, "tools",
                                       "merge_hygiene_baseline.txt")
            try:
                bad = mh.check_parses(mh.tracked_files())
            finally:
                mh.BASELINE = os.path.join(mh.REPO, "tools",
                                           "merge_hygiene_baseline.txt")
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("ledger/b.yaml", bad[0])

    # A record the schema-supersession registry retired and replaced is not a
    # hidden defect -- it is a disclosed one, already routed to a record that
    # parses. Seven such records held `main` red on ten consecutive merges,
    # with neither other route open: editing them is what the registry exists
    # to forbid, and the baseline may only ever shrink. The exemption is
    # therefore VERIFIED rather than trusted, and these pin both directions.

    def _registry(self, repo, **over):
        entry = {
            "kind": "ledger",
            "superseded_path": "ledger/old.yaml",
            "superseded_sha256": mh._sha256_of(os.path.join(repo.path, "ledger/old.yaml")),
            "superseding_path": "ledger/corrections/old.v2.yaml",
            "superseding_sha256": mh._sha256_of(
                os.path.join(repo.path, "ledger/corrections/old.v2.yaml")),
        }
        entry.update(over)
        import yaml
        repo.write("tools/schema_supersession_registry.yaml",
                   yaml.safe_dump({"schema": "schema-supersession-registry-v1",
                                   "records": [entry]}))
        repo.commit()
        mh.SCHEMA_SUPERSESSION_REGISTRY = os.path.join(
            repo.path, "tools", "schema_supersession_registry.yaml")

    def _scene(self, repo, *, replacement="value: fine\n"):
        repo.write("ledger/old.yaml", "broken: [unterminated\n")
        repo.write("ledger/corrections/old.v2.yaml", replacement)
        repo.commit()

    def _run(self, repo):
        keep = mh.SCHEMA_SUPERSESSION_REGISTRY
        try:
            return mh.check_parses(mh.tracked_files())
        finally:
            mh.SCHEMA_SUPERSESSION_REGISTRY = keep

    def test_superseded_record_with_a_parsing_replacement_is_exempt(self) -> None:
        with _Repo() as r:
            self._scene(r)
            self._registry(r)
            self.assertEqual(self._run(r), [])

    def test_exemption_dies_if_the_broken_original_was_touched(self) -> None:
        with _Repo() as r:
            self._scene(r)
            self._registry(r, superseded_sha256="0" * 64)
            bad = self._run(r)
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("ledger/old.yaml", bad[0])

    def test_exemption_dies_if_the_replacement_was_touched(self) -> None:
        with _Repo() as r:
            self._scene(r)
            self._registry(r, superseding_sha256="0" * 64)
            bad = self._run(r)
            self.assertEqual(len(bad), 1, bad)

    def test_exemption_dies_if_the_replacement_does_not_parse(self) -> None:
        # The whole justification is that the content survives in a readable
        # record. A replacement that does not parse is not a replacement.
        with _Repo() as r:
            self._scene(r, replacement="also: [broken\n")
            self._registry(r)
            bad = "\n".join(self._run(r))
            # BOTH are reported: the original loses its exemption, and the
            # replacement is a broken record in its own right.
            self.assertIn("ledger/old.yaml", bad)
            self.assertIn("ledger/corrections/old.v2.yaml", bad)

    def test_an_unregistered_broken_record_is_still_reported(self) -> None:
        with _Repo() as r:
            self._scene(r)
            r.write("ledger/unrelated.yaml", "nope: [broken\n")
            self._registry(r)
            bad = self._run(r)
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("ledger/unrelated.yaml", bad[0])

    def test_malformed_json_queue_is_caught(self) -> None:
        with _Repo() as r:
            r.write("coordination/goals/G/batches/B/dispatch_queue.json",
                    '{"tasks": [ }')
            r.commit()
            bad = mh.check_parses(mh.tracked_files())
            self.assertEqual(len(bad), 1, bad)


class CollisionTests(unittest.TestCase):
    def _binary_collision(self, published: bytes, candidate: bytes) -> list[str]:
        with _Repo() as r:
            r.write("README.md", "base\n")
            r.commit("base")
            git(r.path, "branch", "-q", "other")
            rel = "experiments/EXP-ICPERF-123abc/reports/report.pdf"
            for branch, payload in (("other", published), ("main", candidate)):
                git(r.path, "checkout", "-q", branch)
                path = Path(r.path, rel)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                r.commit(branch)
            return mh.check_collisions("other")

    def test_identical_binary_artifact_is_not_a_collision(self) -> None:
        payload = b"%PDF-1.7\n%\x80\x81\x82\x83\n"
        self.assertEqual(self._binary_collision(payload, payload), [])

    def test_changed_binary_artifact_is_a_collision(self) -> None:
        bad = self._binary_collision(b"%PDF-1.7\n%\x80\x81\n",
                                     b"%PDF-1.7\n%\x80\x82\n")
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("report.pdf: identifier report is already published", bad[0])
        self.assertIn("Do not resolve this by choosing a side", bad[0])

    def test_line_ending_changes_are_not_byte_identical(self) -> None:
        bad = self._binary_collision(b"same text\r\n", b"same text\n")
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("different content", bad[0])

    def test_catches_the_id_allocated_twice(self) -> None:
        """Both branches grepped their own tree correctly. Both got 004."""
        with _Repo() as r:
            r.write("README.md", "base\n")
            r.commit("base")
            git(r.path, "branch", "-q", "other")

            # main spends DEC-20260728-004 on the BATCH-003 support ruling.
            git(r.path, "checkout", "-q", "other")
            r.write("ledger/decisions/DEC-20260728-004.yaml",
                    "coordinator_decision:\n  id: DEC-20260728-004\n"
                    "  decision: support\n")
            r.commit("other allocates 004")

            # The branch spends it on an unrelated BATCH-002 close-out.
            git(r.path, "checkout", "-q", "main")
            r.write("ledger/decisions/DEC-20260728-004.yaml",
                    "coordinator_decision:\n  id: DEC-20260728-004\n"
                    "  decision: revise\n")
            r.commit("branch allocates 004")

            bad = mh.check_collisions("other")
            self.assertEqual(len(bad), 1, bad)
            self.assertIn("already published", bad[0])
            self.assertIn("Do not resolve this by choosing a side", bad[0])

    def test_identical_content_is_not_a_collision(self) -> None:
        with _Repo() as r:
            r.write("README.md", "base\n")
            r.commit("base")
            git(r.path, "branch", "-q", "other")
            same = "coordinator_decision:\n  id: DEC-1\n"
            git(r.path, "checkout", "-q", "other")
            r.write("ledger/decisions/DEC-1.yaml", same)
            r.commit("other")
            git(r.path, "checkout", "-q", "main")
            r.write("ledger/decisions/DEC-1.yaml", same)
            r.commit("branch")
            self.assertEqual(mh.check_collisions("other"), [])

    def test_missing_ref_is_reported_not_crashed(self) -> None:
        with _Repo() as r:
            r.write("README.md", "x\n")
            r.commit()
            out = mh.check_collisions("origin/nonexistent")
            self.assertTrue(out and out[0].startswith("SKIPPED:"), out)


class RegistryDuplicateKeyTests(unittest.TestCase):
    """Merge 21acbaab63 dropped two entries' `- kind:` lines; their keys folded
    into the previous entry and yaml kept the last value, so one supersession
    was shadowed and another lost its route, with every gate passing
    (sheriff case SHF-20261028-0f3f64, LGN-1)."""

    ENTRY = ("- kind: ledger\n"
             "  superseded_path: ledger/decisions/DEC-1.yaml\n"
             "  superseded_sha256: {a}\n"
             "  registered: '2026-10-20'\n").format(a="a" * 64)
    FOLDED = ("  superseded_path: ledger/handoffs/TASK-1.yaml\n"
              "  superseded_sha256: {b}\n").format(b="b" * 64)

    def test_folded_entry_in_either_registry_is_caught(self) -> None:
        for rel, header in (("tools/schema_supersession_registry.yaml",
                             "schema: schema-supersession-registry-v1\n"),
                            ("tools/run_supersession_registry.yaml",
                             "schema: run-supersession-registry-v1\n")):
            with self.subTest(registry=rel), _Repo() as r:
                r.write(rel, header + "records:\n" + self.ENTRY + self.FOLDED)
                r.commit()
                bad = mh.check_registry_duplicate_keys()
                self.assertEqual(len(bad), 1, bad)
                self.assertIn(rel, bad[0])
                self.assertIn("duplicate YAML key", bad[0])
                self.assertIn("superseded_path", bad[0])

    def test_separate_entries_pass(self) -> None:
        with _Repo() as r:
            r.write("tools/schema_supersession_registry.yaml",
                    "schema: schema-supersession-registry-v1\nrecords:\n"
                    + self.ENTRY + "- kind: ledger\n" + self.FOLDED)
            r.commit()
            self.assertEqual(mh.check_registry_duplicate_keys(), [])

    def test_committed_registries_have_no_duplicate_keys(self) -> None:
        self.assertEqual(mh.check_registry_duplicate_keys(), [])


class NewRunManifestTests(unittest.TestCase):
    """Run records failing the schema entered main through PRs merged while
    the relative ledger gate was red or still running (#2452, #2579;
    SHF-20261028-0f3f64, LGN-8). The cheap gate checks the run manifests a
    branch adds or changes; records already on main are never reported."""

    RUN = "experiments/EXP-SUP-001/runs/RUN-SUP-001"
    ARTIFACTS = ("command.txt", "environment.json", "stdout.log", "stderr.log",
                 "raw-result.json")

    def body(self, **drop) -> str:
        import yaml
        body = {"id": "RUN-SUP-001", "experiment_id": "EXP-SUP-001",
                "status": "completed_valid",
                "code": {"commit": "0" * 40, "command": "python3 driver.py"},
                "environment": {"python": "3.13.0"},
                "inputs": {"parameters": {"field_bits": 16}},
                "timing": {"wall_clock_seconds": 1.0},
                "result": {"certificate": {"kind": "none"}}}
        for key in drop:
            body.pop(key)
        return yaml.safe_dump({"run": body}, sort_keys=False)

    def run_dir(self, r) -> None:
        for name in self.ARTIFACTS:
            r.write(f"{self.RUN}/{name}", "{}\n")

    def test_partial_envelope_a_branch_adds_is_caught(self) -> None:
        with _Repo() as r:
            self.run_dir(r)
            r.write(f"{self.RUN}/manifest.yaml", self.body(environment=1, inputs=1))
            r.commit()
            bad = mh.check_new_run_manifests([f"{self.RUN}/manifest.yaml"])
            self.assertIn(f"{self.RUN}/manifest.yaml: run missing required field "
                          "'environment'", bad)
            self.assertIn("supersed", bad[-1])

    def test_empty_manifest_a_branch_adds_is_caught(self) -> None:
        with _Repo() as r:
            self.run_dir(r)
            r.write(f"{self.RUN}/manifest.yaml", "")
            r.commit()
            bad = mh.check_new_run_manifests([f"{self.RUN}/manifest.yaml"])
            self.assertTrue(any("run manifest is empty" in p for p in bad), bad)

    def test_valid_manifest_and_untouched_records_pass(self) -> None:
        with _Repo() as r:
            self.run_dir(r)
            r.write(f"{self.RUN}/manifest.yaml", self.body())
            r.write("experiments/EXP-OLD-001/runs/RUN-OLD-001/manifest.yaml",
                    "run: {id: RUN-OLD-001}\n")
            r.commit()
            self.assertEqual(mh.check_new_run_manifests(
                [f"{self.RUN}/manifest.yaml", "ledger/decisions/DEC-1.yaml"]), [])

    def test_deleted_manifest_is_left_to_the_immutability_check(self) -> None:
        with _Repo() as r:
            r.write("README.md", "x\n")
            r.commit()
            self.assertEqual(mh.check_new_run_manifests([f"{self.RUN}/manifest.yaml"]), [])

    def test_main_runs_it_only_when_scoped(self) -> None:
        with _Repo() as r:
            r.write("ledger/goals/README.md", "goals\n")
            r.write("experiments/EXP-OLD-001/runs/RUN-OLD-001/manifest.yaml",
                    "run: {id: RUN-OLD-001}\n")
            r.commit("base: a pre-existing defective record")
            git(r.path, "branch", "-q", "base")
            with mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--absolute"]):
                self.assertEqual(mh.main(), 0)
            with mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--base", "base"]):
                self.assertEqual(mh.main(), 0)
            self.run_dir(r)
            r.write(f"{self.RUN}/manifest.yaml", self.body(environment=1))
            r.commit("branch adds a defective record")
            with mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--base", "base"]):
                self.assertEqual(mh.main(), 1)


class SessionFileTests(unittest.TestCase):
    """Merge 0186e97db6 spliced two executions of RBS-ICPERF-b7e41c: the
    journal conflicts went to execution B, while B's empty supervisor.stderr
    merged cleanly against an empty merge base, so git kept A's 96 bytes and
    no check failed (DEC-20261029-9bc3ff, TASK-20261029-583a07)."""

    SESSION = "experiments/EXP-T-1/runbook-sessions/RBS-T-abc123"
    STDERR = "steps/S02-trials.attempt-1.supervisor.stderr"
    STDOUT = "steps/S02-trials.attempt-1.supervisor.stdout"

    def write_session(self, r, files: dict[str, str], *, extra=(),
                      session: str | None = None) -> None:
        """Files plus a journal binding exactly their digests."""
        import hashlib
        import json
        session = session or self.SESSION
        logs = [{"path": f"{session}/{name}",
                 "sha256": hashlib.sha256(text.encode()).hexdigest()}
                for name, text in sorted(files.items())]
        lines = [{"seq": 0, "type": "session_started"},
                 {"seq": 1, "type": "step_finished", "logs": logs, "outputs": []},
                 *extra]
        for name, text in files.items():
            r.write(f"{session}/{name}", text)
        r.write(f"{session}/journal.jsonl",
                "".join(json.dumps(line) + "\n" for line in lines))

    def scene(self, r) -> None:
        r.write("README.md", "base\n")
        r.write("ledger/goals/README.md", "goals\n")
        r.commit("base")
        self.write_session(r, {self.STDERR: "", self.STDOUT: "B\n"})
        r.commit("execution B on main")
        git(r.path, "branch", "-q", "base")
        git(r.path, "checkout", "-q", "-b", "pr")

    def check(self, base="base") -> list[str]:
        return mh.check_session_files(base)

    def test_new_session_is_allowed(self) -> None:
        with _Repo() as r:
            self.scene(r)
            self.write_session(r, {self.STDERR: "", self.STDOUT: "new\n"},
                               session="experiments/EXP-T-2/runbook-sessions/RBS-T-def456")
            r.commit("a brand-new session")
            self.assertEqual(self.check(), [])
            with mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--base", "base"]):
                self.assertEqual(mh.main(), 0)

    def test_changing_a_session_file_fails(self) -> None:
        with _Repo() as r:
            self.scene(r)
            r.write(f"{self.SESSION}/{self.STDOUT}", "edited\n")
            r.commit("edit")
            bad = "\n".join(self.check())
            self.assertIn(f"RBS-T-abc123: {self.STDOUT}: session file changed", bad)
            self.assertIn("off its journal digest", bad)
            with mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--base", "base"]):
                self.assertEqual(mh.main(), 1)

    def test_deleting_a_session_file_fails(self) -> None:
        with _Repo() as r:
            self.scene(r)
            git(r.path, "rm", "-q", f"{self.SESSION}/{self.STDOUT}")
            r.commit("delete")
            bad = "\n".join(self.check())
            self.assertIn(f"{self.STDOUT}: present on merge base", bad)
            self.assertIn("deleted on head", bad)
            self.assertIn("recorded by the journal", bad)

    def test_rewriting_the_journal_fails_and_appending_passes(self) -> None:
        with _Repo() as r:
            self.scene(r)
            journal = Path(r.path, self.SESSION, "journal.jsonl")
            original = journal.read_text()
            journal.write_text(original + '{"seq": 2, "type": "session_finished"}\n')
            r.commit("append")
            self.assertEqual(self.check(), [])
            journal.write_text(original.replace('"seq": 0', '"seq": 0, "x": 1'))
            r.commit("rewrite")
            bad = "\n".join(self.check())
            self.assertIn("journal.jsonl: journal rewritten, not appended to", bad)

    def test_file_off_its_journal_digest_fails(self) -> None:
        # The digest check alone: the session is new on this branch, so there
        # is nothing on the base to preserve, but it must match its journal.
        with _Repo() as r:
            self.scene(r)
            other = "experiments/EXP-T-2/runbook-sessions/RBS-T-def456"
            self.write_session(r, {self.STDERR: ""}, session=other)
            r.write(f"{other}/{self.STDERR}", "late write\n")
            r.commit("new session off its journal")
            bad = "\n".join(self.check())
            self.assertIn(f"RBS-T-def456: {self.STDERR}: file is off its journal digest", bad)

    def splice(self, r) -> str:
        """Reconstruct 0186e97db6: A and B both add the session; merging B
        into A resolves the journal to B and keeps A's stderr silently."""
        r.write("README.md", "base\n")
        r.write("ledger/goals/README.md", "goals\n")
        r.commit("base")
        git(r.path, "branch", "-q", "exec-a")
        self.write_session(r, {self.STDERR: "", self.STDOUT: "B\n"})
        r.commit("execution B on main")
        git(r.path, "checkout", "-q", "exec-a")
        self.write_session(r, {self.STDERR: "supervisor: exit 2 impediment\n",
                               self.STDOUT: "B\n"})
        r.commit("execution A")
        subprocess.run(("git", "merge", "-q", "--no-edit", "-X", "theirs", "main"),
                       cwd=r.path, capture_output=True, check=True)
        stderr = Path(r.path, self.SESSION, self.STDERR).read_text()
        self.assertEqual(stderr, "supervisor: exit 2 impediment\n",
                         "git must keep A's stderr without a conflict")
        return git(r.path, "rev-parse", "HEAD").stdout.strip()

    def test_b7e41c_splice_fails_against_the_base(self) -> None:
        with _Repo() as r:
            self.splice(r)
            bad = "\n".join(self.check("main"))
            empty = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            self.assertIn(f"RBS-T-abc123: {self.STDERR}: session file changed: "
                          f"sha256 {empty}", bad)
            self.assertIn(f"journal records sha256 {empty}", bad)

    def test_b7e41c_splice_fails_as_a_merge_commit(self) -> None:
        # No --base: the push-to-main and health sweeps see only the commit.
        with _Repo() as r:
            merge = self.splice(r)
            bad = "\n".join(self.check(None))
            self.assertIn(f"{self.STDERR}: session file changed", bad)
            self.assertIn("merge parent", bad)
            self.assertIn(f"head {merge[:12]}", bad)
            with mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--absolute"]):
                self.assertEqual(mh.main(), 1)

    def test_staged_splice_fails_before_commit(self) -> None:
        with _Repo() as r:
            r.write("README.md", "base\n")
            r.commit("base")
            git(r.path, "branch", "-q", "exec-a")
            self.write_session(r, {self.STDERR: ""})
            r.commit("B")
            git(r.path, "checkout", "-q", "exec-a")
            self.write_session(r, {self.STDERR: "A\n"})
            r.commit("A")
            subprocess.run(("git", "merge", "--no-commit", "-X", "theirs", "main"),
                           cwd=r.path, capture_output=True, check=True)
            self.assertIn(f"{self.STDERR}: session file changed", "\n".join(self.check(None)))

    def test_clean_merge_of_an_appended_journal_passes(self) -> None:
        with _Repo() as r:
            self.scene(r)
            r.write("other.txt", "x\n")
            r.commit("pr work")
            git(r.path, "checkout", "-q", "base")
            journal = Path(r.path, self.SESSION, "journal.jsonl")
            journal.write_text(journal.read_text() + '{"seq": 2, "type": "session_finished"}\n')
            r.commit("session resumed on main")
            git(r.path, "checkout", "-q", "pr")
            git(r.path, "merge", "-q", "--no-edit", "base")
            self.assertEqual(self.check("base"), [])
            self.assertEqual(self.check(None), [])

    def test_known_mismatch_points_at_its_correction(self) -> None:
        path = f"{self.SESSION}/{self.STDERR}"
        with _Repo() as r, mock.patch.dict(mh.KNOWN_SESSION_MISMATCHES,
                                           {path: "ledger/corrections/CORR-X.yaml"}):
            self.scene(r)
            self.assertEqual(self.check(), [], "untouched: never reported")
            r.write(path, "spliced\n")
            r.commit("touch")
            bad = "\n".join(self.check())
            self.assertIn("annotated by ledger/corrections/CORR-X.yaml", bad)

    def test_artifact_store_pointer_digest_is_compared(self) -> None:
        import json
        with _Repo() as r:
            self.scene(r)
            other = "experiments/EXP-T-2/runbook-sessions/RBS-T-def456"
            self.write_session(r, {self.STDERR: "big\n"}, session=other)
            os.remove(os.path.join(r.path, other, self.STDERR))
            import hashlib
            digest = hashlib.sha256(b"big\n").hexdigest()
            r.write(f"{other}/{self.STDERR}.blob.json",
                    json.dumps({"content_sha256": digest, "sha256": "0" * 64}))
            r.commit("stored")
            self.assertEqual(self.check(), [])
            r.write(f"{other}/{self.STDERR}.blob.json",
                    json.dumps({"content_sha256": "1" * 64}))
            r.commit("pointer drift")
            self.assertIn("off its journal digest", "\n".join(self.check()))

    def test_examples_sessions_are_covered(self) -> None:
        with _Repo() as r:
            session = "examples/runbooks/toy/runbook-sessions/RBS-EXAMPLE-1"
            r.write("README.md", "base\n")
            r.commit("base")
            self.write_session(r, {self.STDOUT: "x\n"}, session=session)
            r.commit("example session")
            git(r.path, "branch", "-q", "base")
            r.write(f"{session}/{self.STDOUT}", "y\n")
            r.commit("edit")
            self.assertIn("RBS-EXAMPLE-1", "\n".join(self.check()))

    def test_main_sessions_match_their_journals_except_the_annotated_one(self) -> None:
        candidate = mh._Candidate("HEAD")
        sessions = {mh._session_of(p) for p in mh._session_blobs_in_index()}
        found = [m for s in sorted(sessions) for m in mh._journal_findings(s, candidate, "HEAD")]
        self.assertTrue(all("CORR-20261029-892bca" in m for m in found), found)


if __name__ == "__main__":
    unittest.main()
