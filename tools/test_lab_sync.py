#!/usr/bin/env python3
"""Tests for the cairn lab bridge (tools/lab_sync.py, orchestration/lab.yaml).

The config checks run everywhere. The end-to-end test needs a cairn binary
(CAIRN_BIN or `cairn` on PATH) and is skipped without one: two scratch
working trees, two labs, a directory remote between them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lab_sync  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
TOOL = Path(__file__).resolve().parent / "lab_sync.py"


def glob_matches(glob: str, path: str) -> bool:
    """cairn's policy glob (src/lab/glob.rs): `**` spans segments, `*` and
    `?` stay inside one. Re-stated here so the config can be checked without
    a binary; the end-to-end test checks the real one."""
    import fnmatch

    def match(pattern: list[str], segments: list[str]) -> bool:
        if not pattern:
            return not segments
        if pattern[0] == "**":
            return any(match(pattern[1:], segments[i:]) for i in range(len(segments) + 1))
        return bool(segments) and fnmatch.fnmatchcase(segments[0], pattern[0]) and match(pattern[1:], segments[1:])

    return match(glob.split("/"), path.split("/"))


def tracked(prefix: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", prefix], cwd=REPO, capture_output=True, text=True, check=True)
    return out.stdout.split()


class ConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = lab_sync.load_config()

    def test_every_write_once_glob_names_records_that_exist(self) -> None:
        # A write-once glob that matches nothing is a typo nobody would notice:
        # the records it meant to protect would sync as mutable.
        paths = tracked("coordination") + tracked("ledger/goals")
        for glob in self.config["policy"]["write_once"]:
            if glob.startswith("coordination/events/"):
                continue  # written by CI on main; a branch may have none yet
            self.assertTrue(any(glob_matches(glob, p) for p in paths), f"{glob} matches no tracked file")

    def test_write_once_paths_are_inside_the_scope(self) -> None:
        # Outside the scope a path never enters the lab, so its policy is dead.
        include = self.config["scope"]["include"]
        for glob in self.config["policy"]["write_once"]:
            probe = glob.replace("**", "x").replace("*", "x")
            if probe.startswith("x/"):
                probe = "coordination/" + probe[2:]
            self.assertTrue(any(glob_matches(inc, probe) for inc in include), f"{glob} is outside scope")

    def test_glob_semantics_match_cairns(self) -> None:
        self.assertTrue(glob_matches("**/claims/*.claim.json", "coordination/goals/G/batches/B/claims/TASK-1.3.claim.json"))
        self.assertFalse(glob_matches("ledger/goals/*/checkpoints/**", "ledger/goals/GOAL-X.yaml"))
        self.assertTrue(glob_matches("ledger/goals/*/checkpoints/**", "ledger/goals/GOAL-X/checkpoints/BATCH-1.yaml"))

    def test_records_edited_in_place_are_not_write_once(self) -> None:
        # Rewritten on branches while work is in progress (measured in
        # orchestration/lab.yaml); their immutability is enforced relative to
        # main, in CI, which a path glob cannot express.
        for path in ("ledger/decisions/DEC-1.yaml", "ledger/evidence/EV-1.yaml",
                     "experiments/EXP-X/runs/RUN-1/progress.log", "ledger/goals/GOAL-X/goal.yaml"):
            self.assertFalse(any(glob_matches(g, path) for g in self.config["policy"]["write_once"]), path)

    def test_bad_config_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "lab.yaml"
            bad.write_text("scope: {include: [ledger/**]}\npolicy: {write_once: [/etc/**]}\n")
            with self.assertRaises(ValueError):
                lab_sync.load_config(bad)


class UnconfiguredTest(unittest.TestCase):
    def test_a_missing_binary_is_exit_3_with_the_reason(self) -> None:
        env = {**os.environ, "CAIRN_BIN": "/nonexistent/cairn"}
        out = subprocess.run([sys.executable, str(TOOL), "push"], env=env, capture_output=True, text=True)
        self.assertEqual(out.returncode, 3, out.stderr)
        self.assertIn("no cairn binary", out.stderr)


def cairn() -> str | None:
    found = os.environ.get("CAIRN_BIN") or shutil.which("cairn")
    return found if found and Path(found).is_file() else None


@unittest.skipUnless(cairn(), "needs a cairn binary (CAIRN_BIN or PATH)")
class EndToEndTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="lab-sync-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        for who in ("a", "b"):
            subprocess.run([cairn(), "lab", "identity", "--out", str(self.tmp / f"{who}.json")],
                           check=True, capture_output=True)
            (self.tmp / f"tree-{who}").mkdir()

    def bridge(self, who: str, *args: str) -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "CAIRN_BIN": cairn(),
            "CAIRN_LAB": str(self.tmp / f"lab-{who}"),
            "CAIRN_LAB_IDENTITY": str(self.tmp / f"{who}.json"),
            "LAB_SYNC_ROOT": str(self.tmp / f"tree-{who}"),
        }
        return subprocess.run([sys.executable, str(TOOL), *args], env=env, capture_output=True, text=True)

    def write(self, who: str, path: str, text: str) -> None:
        target = self.tmp / f"tree-{who}" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def test_two_sessions_share_state_without_git(self) -> None:
        goal = "ledger/goals/GOAL-T-0000ab/goal.yaml"
        claim = "coordination/goals/GOAL-T-0000ab/batches/BATCH-00cdef/claims/TASK-20261002-aaaaaa.1.claim.json"
        self.write("a", goal, "status: active\n")
        self.write("a", claim, json.dumps({"holder": "executor-1"}))
        self.write("a", "tools/not_in_scope.py", "print('code stays in git')\n")
        self.write("a", "knowledge/INDEX.md", "generated\n")
        self.assertEqual(self.bridge("a", "init").returncode, 0)
        pushed = self.bridge("a", "push")
        self.assertEqual(pushed.returncode, 0, pushed.stdout + pushed.stderr)

        # b starts from a's directory and pulls the state.
        space = json.loads(subprocess.run([cairn(), "lab", "--lab", str(self.tmp / "lab-a"), "status", "--json"],
                                          capture_output=True, text=True, check=True).stdout)["space"]
        subprocess.run([cairn(), "lab", "--lab", str(self.tmp / "lab-b"), "clone", "--space", space,
                        "--dir", str(self.tmp / "lab-a")], check=True, capture_output=True)
        b_key = json.loads((self.tmp / "b.json").read_text())["public"]
        subprocess.run([cairn(), "lab", "--lab", str(self.tmp / "lab-a"), "admit", b_key, "--roles", "writer",
                        "--identity", str(self.tmp / "a.json")], check=True, capture_output=True)
        pulled = self.bridge("b", "pull", "--remote", f"dir:{self.tmp / 'lab-a'}")
        self.assertEqual(pulled.returncode, 0, pulled.stdout + pulled.stderr)
        tree_b = self.tmp / "tree-b"
        self.assertEqual((tree_b / goal).read_text(), "status: active\n")
        self.assertTrue((tree_b / claim).is_file())
        self.assertFalse((tree_b / "tools/not_in_scope.py").exists(), "code is not in scope")
        self.assertFalse((tree_b / "knowledge/INDEX.md").exists(), "generated files never enter")

        # A write-once claim cannot be edited: refused before signing, exit 2.
        self.write("b", claim, json.dumps({"holder": "executor-2"}))
        refused = self.bridge("b", "push")
        self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)

        # Concurrent edits of one goal head: a visible conflict on both sides.
        self.write("a", goal, "status: active\nnext_action: run\n")
        self.write("b", goal, "status: active\nnext_action: design\n")
        self.assertEqual(self.bridge("a", "push").returncode, 0)
        synced = self.bridge("b", "sync", "--remote", f"dir:{self.tmp / 'lab-a'}")
        # b's refused claim edit is still on disk, so its push reports 2; the
        # conflict makes the pull report 1. Either way the sync is not clean.
        self.assertNotEqual(synced.returncode, 0)
        self.assertIn("open conflict", synced.stdout)
        sidecars = list((tree_b / "ledger/goals/GOAL-T-0000ab").glob("goal.yaml.lab-conflict-*"))
        self.assertEqual(len(sidecars), 1)


if __name__ == "__main__":
    unittest.main()
