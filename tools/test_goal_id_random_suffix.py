#!/usr/bin/env python3
"""Prospective random-suffix GOAL identifier merge-hygiene tests."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_merge_hygiene as hygiene
import validate_ledger as vl


class ProspectiveGoalIdentifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.external_temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.external_root = Path(self.external_temporary.name)
        self.git("init", "-q")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Goal Identifier Tests")
        self._write_goal("GOAL-BASE-001", sharded=False)
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.git("tag", "base-tree")
        tools = self.root / "tools"
        tools.mkdir(exist_ok=True)
        self.cli = tools / "check_merge_hygiene.py"
        shutil.copy2(Path(hygiene.__file__), self.cli)
        shutil.copy2(Path(vl.__file__), tools / "validate_ledger.py")

    def tearDown(self) -> None:
        self.external_temporary.cleanup()
        self.temporary.cleanup()

    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _write_goal(self, goal_id: str, *, sharded: bool) -> Path:
        path = (self.root / "ledger/goals" / goal_id / "goal.yaml"
                if sharded
                else self.root / "ledger/goals" / f"{goal_id}.yaml")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"research_goal:\n  id: {goal_id}\n  status: active\n",
            encoding="utf-8",
        )
        return path

    @staticmethod
    def _goal_document(goal_id: str) -> str:
        return f"""research_goal:
  id: {goal_id}
  title: symlink fixture
  objective: prove goal targets are not followed
  question_ids: []
  status: active
  completion_criteria: [done]
  pause_conditions: [stop]
  next_action: retain the fixture boundary
  owner: coordinator
"""

    def _problems(self) -> list[str]:
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            return hygiene.check_prospective_goal_ids("base-tree")

    def _symlink_problems(self) -> list[str]:
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            return hygiene.check_goal_symlinks(hygiene.tracked_files())

    def _validator_context(self) -> vl.Ctx:
        context = vl.Ctx(set())
        with mock.patch.object(vl, "REPO", str(self.root)):
            vl.check_goals(context)
        return context

    def _run_base_cli(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.cli), "--base", "base-tree"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def _run_validator_cli(
        self, environment: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(environment or {})
        return subprocess.run(
            [sys.executable, str(self.root / "tools/validate_ledger.py")],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def _prefix_target(self, prefix: str, kind: str) -> Path:
        if kind == "internal":
            target = self.root / "prefix-fixtures" / prefix.replace("/", "-")
        else:
            target = self.external_root / f"{kind}-{prefix.replace('/', '-')}"
        if kind == "dangling":
            return target
        goals = target / "goals" if prefix == "ledger" else target
        goals.mkdir(parents=True)
        (goals / "GOAL-HIDDEN-999.yaml").write_text(
            self._goal_document("GOAL-HIDDEN-999"), encoding="utf-8"
        )
        (goals / "GOAL-HIDDEN-a1b2c3.yaml").write_text(
            self._goal_document("GOAL-HIDDEN-a1b2c3"), encoding="utf-8"
        )
        (goals / "GOAL-PARSE-deadbe.yaml").write_text(
            "B2_TARGET_ONLY_PARSE_MARKER: [unterminated\n", encoding="utf-8"
        )
        return target

    def _replace_prefix(self, prefix: str, kind: str, *, stage: bool,
                        commit: bool = False) -> Path:
        path = self.root.joinpath(*prefix.split("/"))
        shutil.rmtree(path)
        target = self._prefix_target(prefix, kind)
        link_target: Path | str = target
        if kind == "internal":
            link_target = os.path.relpath(target, path.parent)
        path.symlink_to(link_target, target_is_directory=True)
        if stage:
            self.git("add", "-A")
        if commit:
            self.git("commit", "-qm", f"{kind} {prefix} alias")
        return path

    def _assert_prefix_rejected(self, prefix: str) -> None:
        merge = self._run_base_cli()
        self.assertEqual(merge.returncode, 1, (merge.stdout, merge.stderr))
        self.assertIn("invalid trusted goal prefixes", merge.stderr)
        self.assertIn(prefix, merge.stderr)
        self.assertIn("target was not read", merge.stderr)
        self.assertNotIn("GOAL-HIDDEN-999", merge.stdout + merge.stderr)
        self.assertNotIn("GOAL-HIDDEN-a1b2c3", merge.stdout + merge.stderr)
        self.assertNotIn("B2_TARGET_ONLY_PARSE_MARKER", merge.stdout + merge.stderr)

        ledger = self._run_validator_cli()
        self.assertEqual(ledger.returncode, 1, (ledger.stdout, ledger.stderr))
        self.assertIn("trusted goal prefix is", ledger.stderr)
        self.assertIn(prefix, ledger.stderr)
        self.assertIn("target was not read", ledger.stderr)
        self.assertNotIn("GOAL-HIDDEN-999", ledger.stdout + ledger.stderr)
        self.assertNotIn("GOAL-HIDDEN-a1b2c3", ledger.stdout + ledger.stderr)
        self.assertNotIn("B2_TARGET_ONLY_PARSE_MARKER", ledger.stdout + ledger.stderr)

        context = self._validator_context()
        self.assertNotIn("GOAL-HIDDEN-999", context.ids)
        self.assertNotIn("GOAL-HIDDEN-a1b2c3", context.ids)
        self.assertTrue(any(prefix in error and "target was not read" in error
                            for error in context.errors), context.errors)

    def _stage_gitlink(self, prefix: str, *, initialized: bool,
                       target_commit: str | None = None) -> Path:
        path = self.root.joinpath(*prefix.split("/"))
        commit = target_commit or self.git("rev-parse", "HEAD")
        self.git("rm", "-qr", "--cached", prefix)
        self.git("update-index", "--add", "--cacheinfo",
                 "160000", commit, prefix)
        if initialized:
            goals = path / "goals" if prefix == "ledger" else path
            goals.mkdir(parents=True, exist_ok=True)
            marker = ("LEDGER_GITLINK_INTERPRETED" if prefix == "ledger"
                      else "GITLINK_TARGET_INTERPRETED")
            legacy = self._goal_document("GOAL-GITLINK-999") + \
                f"  target_marker: {marker}\n"
            random_goal = self._goal_document("GOAL-GITLINK-a1b2c3") + \
                f"  target_marker: {marker}\n"
            (goals / "GOAL-GITLINK-999.yaml").write_text(
                legacy, encoding="utf-8"
            )
            (goals / "GOAL-GITLINK-a1b2c3.yaml").write_text(
                random_goal, encoding="utf-8"
            )
            (goals / "GOAL-MALFORMED-deadbe.yaml").write_text(
                "TARGET_ONLY_MALFORMED_YAML: [unterminated\n", encoding="utf-8"
            )
        else:
            shutil.rmtree(path)
        return path

    def _assert_gitlink_rejected(
        self, prefix: str, marker: str,
        environment: dict[str, str] | None = None,
    ) -> None:
        result = self._run_validator_cli(environment)
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        combined = result.stdout + result.stderr
        self.assertIn("exact Git", combined)
        self.assertIn("gitlink", combined)
        self.assertIn("160000", combined)
        self.assertIn("target was not read", combined)
        self.assertNotIn("GOAL-GITLINK-999", combined)
        self.assertNotIn("GOAL-GITLINK-a1b2c3", combined)
        self.assertNotIn(marker, combined)
        self.assertNotIn("TARGET_ONLY_MALFORMED_YAML", combined)

        with mock.patch.dict(os.environ, environment or {}, clear=False):
            context = self._validator_context()
        self.assertNotIn("GOAL-GITLINK-999", context.ids)
        self.assertNotIn("GOAL-GITLINK-a1b2c3", context.ids)
        self.assertNotIn(marker, repr(context.records))
        self.assertFalse(any("TARGET_ONLY_MALFORMED_YAML" in error
                             for error in context.errors), context.errors)
        self.assertTrue(any("exact Git" in error and "gitlink" in error
                            for error in context.errors), context.errors)

        merge = self._run_base_cli()
        self.assertEqual(merge.returncode, 1, (merge.stdout, merge.stderr))
        self.assertIn("160000", merge.stderr)

    def _alternate_index(self, ref: str = "base-tree") -> Path:
        index = self.external_root / f"alternate-index-{len(list(self.external_root.iterdir()))}"
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(index)
        subprocess.run(
            ["git", "-C", str(self.root), "read-tree", ref],
            check=True, capture_output=True, text=True, env=env,
        )
        return index

    def _benign_repository(self) -> Path:
        root = self.external_root / "benign-repository"
        root.mkdir()
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", str(root), "config", "user.email",
             "tests@example.invalid"], check=True
        )
        subprocess.run(
            ["git", "-C", str(root), "config", "user.name", "Benign Git"],
            check=True,
        )
        path = root / "ledger/goals/GOAL-BENIGN-a1b2c3.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(
            "research_goal:\n  id: GOAL-BENIGN-a1b2c3\n  status: active\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(root), "commit", "-qm", "benign"], check=True
        )
        return root

    def _install_replace(
        self, original: str, replacement: str, *, ref_base: str = "refs/replace"
    ) -> str:
        ref = f"{ref_base.rstrip('/')}/{original}"
        self.git("update-ref", ref, replacement)
        return ref

    def _effective_tree_mode(
        self, prefix: str, environment: dict[str, str] | None = None
    ) -> str:
        env = os.environ.copy()
        env.pop("GIT_NO_REPLACE_OBJECTS", None)
        env.update(environment or {})
        result = subprocess.run(
            ["git", "-C", str(self.root), "ls-tree", "HEAD", "--", prefix],
            check=True, capture_output=True, text=True, env=env,
        )
        metadata = result.stdout.split("\t", 1)[0]
        return metadata.split(" ", 1)[0]

    def _assert_replace_ref_preserved(self, ref: str, expected: str) -> None:
        self.assertEqual(self.git("rev-parse", ref), expected)

    def _assert_base_cli_rejects_symlink(self) -> subprocess.CompletedProcess[str]:
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("symlinked goal paths", result.stderr)
        return result

    def _assert_merge_hygiene_rejects(self) -> None:
        output = StringIO()
        error = StringIO()
        with (mock.patch.object(hygiene, "REPO", str(self.root)),
              mock.patch.object(hygiene, "BASELINE",
                                str(self.root / "missing-baseline.txt")),
              mock.patch.object(sys, "argv", ["check_merge_hygiene.py", "--absolute"]),
              redirect_stdout(output), redirect_stderr(error)):
            status = hygiene.main()
        self.assertEqual(status, 1)
        self.assertIn("symlinked goal paths", error.getvalue())

    def test_flat_to_sharded_legacy_migration_is_not_new_minting(self) -> None:
        (self.root / "ledger/goals/GOAL-BASE-001.yaml").unlink()
        self._write_goal("GOAL-BASE-001", sharded=True)
        self.git("add", "-A")
        self.assertEqual(self._problems(), [])

    def test_new_legacy_flat_goal_is_rejected_from_staged_worktree(self) -> None:
        self._write_goal("GOAL-NEW-002", sharded=False)
        self.git("add", "ledger/goals/GOAL-NEW-002.yaml")
        problems = self._problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("GOAL-NEW-002", problems[0])

    def test_new_legacy_sharded_goal_is_rejected_after_commit(self) -> None:
        self._write_goal("GOAL-NEW-003", sharded=True)
        self.git("add", ".")
        self.git("commit", "-qm", "new legacy shard")
        problems = self._problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("GOAL-NEW-003", problems[0])

    def test_new_random_flat_and_sharded_goals_are_allowed(self) -> None:
        self._write_goal("GOAL-NEW-a1b2c3", sharded=False)
        self._write_goal("GOAL-NEW-deadbe", sharded=True)
        self.git("add", ".")
        self.assertEqual(self._problems(), [])

    def test_noncanonical_new_goal_is_rejected_prospectively(self) -> None:
        self._write_goal("GOAL-NEW-abcd", sharded=False)
        self.git("add", ".")
        problems = self._problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("GOAL-NEW-abcd", problems[0])

    def test_only_flat_and_sharded_heads_define_semantic_goals(self) -> None:
        paths = [
            "ledger/goals/GOAL-X-a1b2c3.yaml",
            "ledger/goals/GOAL-Y-deadbe/goal.yaml",
            "ledger/goals/GOAL-Z-001/checkpoints/BATCH-001.yaml",
        ]
        self.assertEqual(
            hygiene.goal_ids_from_paths(paths),
            {"GOAL-X-a1b2c3", "GOAL-Y-deadbe"},
        )

    def test_committed_external_goals_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger/goals", "external", stage=True, commit=True)
        self._assert_prefix_rejected("ledger/goals")

    def test_committed_internal_goals_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger/goals", "internal", stage=True, commit=True)
        self._assert_prefix_rejected("ledger/goals")

    def test_committed_dangling_goals_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger/goals", "dangling", stage=True, commit=True)
        self._assert_prefix_rejected("ledger/goals")

    def test_committed_external_ledger_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger", "external", stage=True, commit=True)
        self._assert_prefix_rejected("ledger")

    def test_committed_initialized_goals_gitlink_is_rejected(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "initialized goals gitlink")
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_committed_initialized_ledger_gitlink_is_rejected(self) -> None:
        self._stage_gitlink("ledger", initialized=True)
        self.git("commit", "-qm", "initialized ledger gitlink")
        self._assert_gitlink_rejected(
            "ledger", "LEDGER_GITLINK_INTERPRETED"
        )

    def test_uninitialized_goals_gitlink_is_rejected(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=False)
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_uninitialized_ledger_gitlink_is_rejected(self) -> None:
        self._stage_gitlink("ledger", initialized=False)
        self._assert_gitlink_rejected(
            "ledger", "LEDGER_GITLINK_INTERPRETED"
        )

    def test_unavailable_target_goals_gitlink_is_rejected(self) -> None:
        self._stage_gitlink(
            "ledger/goals", initialized=False, target_commit="a" * 40
        )
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_unavailable_target_ledger_gitlink_is_rejected(self) -> None:
        self._stage_gitlink(
            "ledger", initialized=False, target_commit="b" * 40
        )
        self._assert_gitlink_rejected(
            "ledger", "LEDGER_GITLINK_INTERPRETED"
        )

    def test_staged_initialized_gitlink_is_rejected(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_staged_gitlink_remains_rejected_after_worktree_disagrees(self) -> None:
        path = self._stage_gitlink("ledger/goals", initialized=False)
        path.mkdir()
        (path / "GOAL-BASE-001.yaml").write_text(
            "research_goal:\n  id: GOAL-BASE-001\n  status: active\n",
            encoding="utf-8",
        )
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_head_goals_gitlink_rejects_candidate_index_descendants(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink in HEAD")
        self.git("read-tree", "base-tree")
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_head_ledger_gitlink_rejects_candidate_index_descendants(self) -> None:
        self._stage_gitlink("ledger", initialized=True)
        self.git("commit", "-qm", "ledger gitlink in HEAD")
        self.git("read-tree", "base-tree")
        self._assert_gitlink_rejected(
            "ledger", "LEDGER_GITLINK_INTERPRETED"
        )

    def test_rename_destination_cannot_authorize_head_gitlink(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink before rename candidate")
        self.git("read-tree", "base-tree")
        source = "ledger/goals/GOAL-BASE-001.yaml"
        destination = "ledger/goals/GOAL-RENAMED-a1b2c3.yaml"
        blob = self.git("rev-parse", f"base-tree:{source}")
        self.git("update-index", "--force-remove", source)
        self.git("update-index", "--add", "--cacheinfo",
                 "100644", blob, destination)
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )

    def test_alternate_index_cannot_mask_explicit_root_gitlink(self) -> None:
        alternate = self._alternate_index()
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "gitlink hidden from alternate index")
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED",
            {"GIT_INDEX_FILE": str(alternate)},
        )

    def test_misleading_git_dir_and_work_tree_cannot_redirect_root(self) -> None:
        benign = self._benign_repository()
        self._stage_gitlink("ledger", initialized=True)
        self.git("commit", "-qm", "gitlink hidden from alternate repository")
        self._assert_gitlink_rejected(
            "ledger", "LEDGER_GITLINK_INTERPRETED",
            {"GIT_DIR": str(benign / ".git"), "GIT_WORK_TREE": str(benign)},
        )

    def test_combined_alternate_git_environment_cannot_redirect_root(self) -> None:
        alternate = self._alternate_index()
        benign = self._benign_repository()
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "gitlink hidden from combined environment")
        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED",
            {
                "GIT_INDEX_FILE": str(alternate),
                "GIT_DIR": str(benign / ".git"),
                "GIT_WORK_TREE": str(benign),
            },
        )

    def test_default_commit_replacement_cannot_launder_goals_gitlink(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink behind commit replacement")
        original = self.git("rev-parse", "HEAD")
        replacement = self.git("rev-parse", "base-tree")
        ref = self._install_replace(original, replacement)
        self.assertEqual(self._effective_tree_mode("ledger/goals"), "040000")

        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )
        self._assert_replace_ref_preserved(ref, replacement)

    def test_default_tree_replacement_cannot_launder_goals_gitlink(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink behind tree replacement")
        original = self.git("rev-parse", "HEAD:ledger")
        replacement = self.git("rev-parse", "base-tree:ledger")
        ref = self._install_replace(original, replacement)
        self.assertEqual(self._effective_tree_mode("ledger/goals"), "040000")

        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED"
        )
        self._assert_replace_ref_preserved(ref, replacement)

    def test_default_tree_replacement_cannot_launder_ledger_gitlink(self) -> None:
        self._stage_gitlink("ledger", initialized=True)
        self.git("commit", "-qm", "ledger gitlink behind tree replacement")
        original = self.git("rev-parse", "HEAD^{tree}")
        replacement = self.git("rev-parse", "base-tree^{tree}")
        ref = self._install_replace(original, replacement)
        self.assertEqual(self._effective_tree_mode("ledger"), "040000")

        self._assert_gitlink_rejected(
            "ledger", "LEDGER_GITLINK_INTERPRETED"
        )
        self._assert_replace_ref_preserved(ref, replacement)

    def test_custom_replace_namespace_cannot_launder_commit(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink behind custom replacement")
        original = self.git("rev-parse", "HEAD")
        replacement = self.git("rev-parse", "base-tree")
        ref_base = "refs/test-replacements"
        ref = self._install_replace(original, replacement, ref_base=ref_base)
        environment = {"GIT_REPLACE_REF_BASE": ref_base}
        self.assertEqual(
            self._effective_tree_mode("ledger/goals", environment), "040000"
        )

        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED", environment
        )
        self._assert_replace_ref_preserved(ref, replacement)

    def test_caller_cannot_reenable_replacements_with_zero(self) -> None:
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink behind caller override")
        original = self.git("rev-parse", "HEAD")
        replacement = self.git("rev-parse", "base-tree")
        ref = self._install_replace(original, replacement)
        environment = {"GIT_NO_REPLACE_OBJECTS": "0"}
        # Git currently treats presence of this variable as disabling replace
        # processing even when its value is "0".  The validator must not rely
        # on that incidental parsing rule: it strips the caller value and
        # installs its own explicit disable on every bound query.
        self.assertEqual(
            self._effective_tree_mode("ledger/goals", environment), "160000"
        )

        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED", environment
        )
        self._assert_replace_ref_preserved(ref, replacement)

    def test_replace_namespace_and_alternate_git_context_cannot_launder(self) -> None:
        alternate = self._alternate_index()
        benign = self._benign_repository()
        self._stage_gitlink("ledger/goals", initialized=True)
        self.git("commit", "-qm", "goals gitlink behind combined redirects")
        original = self.git("rev-parse", "HEAD")
        replacement = self.git("rev-parse", "base-tree")
        ref_base = "refs/combined-replacements"
        ref = self._install_replace(original, replacement, ref_base=ref_base)
        replacement_environment = {"GIT_REPLACE_REF_BASE": ref_base}
        self.assertEqual(
            self._effective_tree_mode("ledger/goals", replacement_environment),
            "040000",
        )
        environment = {
            **replacement_environment,
            "GIT_NO_REPLACE_OBJECTS": "0",
            "GIT_INDEX_FILE": str(alternate),
            "GIT_DIR": str(benign / ".git"),
            "GIT_WORK_TREE": str(benign),
        }

        self._assert_gitlink_rejected(
            "ledger/goals", "GITLINK_TARGET_INTERPRETED", environment
        )
        self._assert_replace_ref_preserved(ref, replacement)

    def test_every_bound_provenance_query_disables_replacements(self) -> None:
        caller_environment = {
            "GIT_REPLACE_REF_BASE": "refs/caller-selected-replacements",
            "GIT_NO_REPLACE_OBJECTS": "0",
        }
        real_run = subprocess.run
        with (mock.patch.dict(os.environ, caller_environment, clear=False),
              mock.patch.object(vl.subprocess, "run", wraps=real_run) as run):
            with mock.patch.object(vl, "REPO", str(self.root)):
                in_git, errors = vl.protected_prefix_git_errors()
        self.assertTrue(in_git)
        self.assertEqual(errors, [])

        provenance_calls = []
        for call in run.call_args_list:
            command = call.args[0]
            if "ls-tree" in command or "ls-files" in command:
                provenance_calls.append(call)
        self.assertEqual(len(provenance_calls), 4)
        for call in provenance_calls:
            command = call.args[0]
            environment = call.kwargs["env"]
            self.assertIn("--no-replace-objects", command)
            self.assertEqual(environment.get("GIT_NO_REPLACE_OBJECTS"), "1")
            self.assertNotIn("GIT_REPLACE_REF_BASE", environment)

    def test_raw_provenance_query_failure_stops_before_traversal(self) -> None:
        probe = subprocess.CompletedProcess([], 0, "true\n", "")
        context = subprocess.CompletedProcess(
            [], 0,
            f"{self.root}\n{self.root / '.git'}\n{self.root / '.git/index'}\n",
            "",
        )
        raw_failure = subprocess.CompletedProcess(
            [], 128, "", "fatal: cannot read raw tree object\n"
        )
        unused_index = subprocess.CompletedProcess([], 0, "", "")
        with mock.patch.object(
            vl.subprocess, "run",
            side_effect=[probe, context, raw_failure, unused_index],
        ):
            rejected = self._validator_context()
        rendered = "\n".join(rejected.errors)
        self.assertIn("cannot determine protected-prefix Git metadata", rendered)
        self.assertIn("target was not read", rendered)
        self.assertNotIn("GOAL-HIDDEN-999", rejected.ids)
        self.assertNotIn("GOAL-HIDDEN-a1b2c3", rejected.ids)

    def test_head_symlink_rejects_index_descendants(self) -> None:
        self._replace_prefix("ledger/goals", "external", stage=True, commit=True)
        self.git("read-tree", "base-tree")
        result = self._run_validator_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("exact Git HEAD tree symlink", result.stderr)
        self.assertIn("target was not read", result.stderr)

    def test_ordinary_descendants_are_not_exact_gitlink_entries(self) -> None:
        with mock.patch.object(vl, "REPO", str(self.root)):
            in_git, errors = vl.protected_prefix_git_errors()
        self.assertTrue(in_git)
        self.assertEqual(errors, [])

    def test_non_git_fixture_uses_filesystem_boundary_only(self) -> None:
        nongit = self.external_root / "non-git-fixture"
        (nongit / "ledger/goals").mkdir(parents=True)
        context = vl.Ctx(set())
        with mock.patch.object(vl, "REPO", str(nongit)):
            in_git, errors = vl.protected_prefix_git_errors()
            valid = vl.check_trusted_goal_prefixes(context)
        self.assertFalse(in_git)
        self.assertEqual(errors, [])
        self.assertTrue(valid)
        self.assertEqual(context.errors, [])

        shutil.rmtree(nongit / "ledger/goals")
        target = self.external_root / "non-git-target"
        target.mkdir()
        (nongit / "ledger/goals").symlink_to(target, target_is_directory=True)
        rejected = vl.Ctx(set())
        with mock.patch.object(vl, "REPO", str(nongit)):
            valid = vl.check_trusted_goal_prefixes(rejected)
        self.assertFalse(valid)
        self.assertTrue(any("trusted goal prefix is symlink" in error
                            for error in rejected.errors), rejected.errors)
        self.assertFalse(any("Git index" in error for error in rejected.errors),
                         rejected.errors)

    def test_committed_internal_ledger_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger", "internal", stage=True, commit=True)
        self._assert_prefix_rejected("ledger")

    def test_committed_dangling_ledger_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger", "dangling", stage=True, commit=True)
        self._assert_prefix_rejected("ledger")

    def test_staged_goals_prefix_alias_is_rejected_from_index(self) -> None:
        self._replace_prefix("ledger/goals", "external", stage=True)
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("staged index is symlink (Git mode 120000)", result.stderr)

    def test_staged_ledger_prefix_alias_is_rejected_from_index(self) -> None:
        self._replace_prefix("ledger", "external", stage=True)
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("staged index is symlink (Git mode 120000)", result.stderr)

    def test_staged_regular_file_prefix_is_rejected(self) -> None:
        path = self.root / "ledger/goals"
        shutil.rmtree(path)
        path.write_text("not a directory\n", encoding="utf-8")
        self.git("add", "-A")
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("staged index is non-directory Git mode 100644",
                      result.stderr)
        ledger = self._run_validator_cli()
        self.assertEqual(ledger.returncode, 1, (ledger.stdout, ledger.stderr))
        self.assertIn("trusted goal prefix is regular file", ledger.stderr)

    def test_missing_required_prefix_is_rejected(self) -> None:
        shutil.rmtree(self.root / "ledger/goals")
        self.git("add", "-A")
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("staged index is missing", result.stderr)
        ledger = self._run_validator_cli()
        self.assertEqual(ledger.returncode, 1, (ledger.stdout, ledger.stderr))
        self.assertIn("trusted goal prefix is missing", ledger.stderr)

    def test_staged_prefix_alias_remains_rejected_after_worktree_diverges(self) -> None:
        path = self._replace_prefix("ledger/goals", "external", stage=True)
        path.unlink()
        path.mkdir()
        (path / "GOAL-BASE-001.yaml").write_text(
            "research_goal:\n  id: GOAL-BASE-001\n  status: active\n",
            encoding="utf-8",
        )
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("staged index is symlink (Git mode 120000)", result.stderr)

    def test_tracked_worktree_goals_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger/goals", "external", stage=False)
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("tracked worktree/absolute tree is symlink", result.stderr)

    def test_tracked_worktree_ledger_prefix_alias_is_rejected(self) -> None:
        self._replace_prefix("ledger", "external", stage=False)
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("tracked worktree/absolute tree is symlink", result.stderr)

    def test_absolute_prefix_check_rejects_without_resolving_target(self) -> None:
        self._replace_prefix("ledger/goals", "external", stage=False)
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            problems = hygiene.check_trusted_goal_prefixes()
        self.assertTrue(problems)
        rendered = "\n".join(problems)
        self.assertIn("tracked worktree/absolute tree is symlink", rendered)
        self.assertNotIn("GOAL-HIDDEN", rendered)

    def test_ordinary_trusted_prefixes_pass_all_candidate_states(self) -> None:
        with mock.patch.object(hygiene, "REPO", str(self.root)):
            self.assertEqual(hygiene.check_trusted_goal_prefixes(), [])
        context = self._validator_context()
        self.assertFalse(any("trusted goal prefix" in error
                             for error in context.errors), context.errors)

    def test_tracked_sharded_directory_symlink_is_rejected_without_follow(self) -> None:
        target = self.external_root / "valid-goal-target"
        target.mkdir()
        (target / "goal.yaml").write_text(
            self._goal_document("GOAL-TARGET-a1b2c3"), encoding="utf-8"
        )
        link = self.root / "ledger/goals/GOAL-BYPASS-002"
        link.symlink_to(target, target_is_directory=True)
        self.git("add", "ledger/goals/GOAL-BYPASS-002")

        problems = self._symlink_problems()
        self.assertTrue(any("GOAL-BYPASS-002" in problem for problem in problems))
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertTrue(any("goal path may not be a symlink" in error
                            for error in context.errors), context.errors)
        self.assertNotIn("GOAL-TARGET-a1b2c3", context.ids)
        self.assertNotIn("GOAL-BYPASS-002", context.ids)

    def test_dangling_sharded_directory_symlink_is_rejected(self) -> None:
        link = self.root / "ledger/goals/GOAL-DANGLING-003"
        link.symlink_to(self.external_root / "missing", target_is_directory=True)
        self.git("add", "ledger/goals/GOAL-DANGLING-003")

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertTrue(any("GOAL-DANGLING-003" in error
                            and "target was not read" in error
                            for error in context.errors), context.errors)

    def test_flat_goal_record_symlink_is_rejected_without_follow(self) -> None:
        target = self.external_root / "flat-target.yaml"
        target.write_text(self._goal_document("GOAL-TARGET-deadbe"), encoding="utf-8")
        link = self.root / "ledger/goals/GOAL-FLAT-a1b2c3.yaml"
        link.symlink_to(target)
        self.git("add", "ledger/goals/GOAL-FLAT-a1b2c3.yaml")

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertNotIn("GOAL-TARGET-deadbe", context.ids)
        self.assertNotIn("GOAL-FLAT-a1b2c3", context.ids)

    def test_nested_sharded_goal_head_symlink_is_rejected_without_follow(self) -> None:
        target = self.external_root / "nested-target.yaml"
        target.write_text(self._goal_document("GOAL-TARGET-c0ffee"), encoding="utf-8")
        link = self.root / "ledger/goals/GOAL-NESTED-a1b2c3/goal.yaml"
        link.parent.mkdir(parents=True)
        link.symlink_to(target)
        self.git("add", "ledger/goals/GOAL-NESTED-a1b2c3/goal.yaml")

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertNotIn("GOAL-TARGET-c0ffee", context.ids)
        self.assertNotIn("GOAL-NESTED-a1b2c3", context.ids)

    def test_symlinked_checkpoint_directory_is_rejected_without_follow(self) -> None:
        goal_id = "GOAL-CHECKPOINT-a1b2c3"
        head = self.root / "ledger/goals" / goal_id / "goal.yaml"
        head.parent.mkdir(parents=True)
        head.write_text(self._goal_document(goal_id), encoding="utf-8")
        target = self.external_root / "checkpoint-target"
        target.mkdir()
        (target / "BATCH-a1b2c3.yaml").write_text(
            "batch_checkpoint:\n  batch_id: BATCH-a1b2c3\n  sentinel: followed\n",
            encoding="utf-8",
        )
        checkpoints = head.parent / "checkpoints"
        checkpoints.symlink_to(target, target_is_directory=True)
        self.git("add", str(head.relative_to(self.root)),
                 str(checkpoints.relative_to(self.root)))

        self.assertTrue(self._symlink_problems())
        self._assert_merge_hygiene_rejects()
        context = self._validator_context()
        self.assertIn(goal_id, context.ids)
        self.assertNotIn("batch_checkpoints", context.records[goal_id])
        self.assertTrue(any("checkpoints" in error and "target was not read" in error
                            for error in context.errors), context.errors)

    def test_base_cli_rejects_staged_added_sharded_directory_symlink(self) -> None:
        target = self.external_root / "staged-shard-target"
        target.mkdir()
        (target / "goal.yaml").write_text(
            self._goal_document("GOAL-STAGED-a1b2c3"), encoding="utf-8"
        )
        link = self.root / "ledger/goals/GOAL-STAGED-a1b2c3"
        link.symlink_to(target, target_is_directory=True)
        self.git("add", str(link.relative_to(self.root)))

        result = self._assert_base_cli_rejects_symlink()
        self.assertIn("staged index (object mode 120000)", result.stderr)

    def test_base_cli_rejects_staged_type_change_to_symlink(self) -> None:
        target = self.external_root / "staged-type-target.yaml"
        target.write_text(
            self._goal_document("GOAL-BASE-001"), encoding="utf-8"
        )
        path = self.root / "ledger/goals/GOAL-BASE-001.yaml"
        path.unlink()
        path.symlink_to(target)
        self.git("add", str(path.relative_to(self.root)))

        result = self._assert_base_cli_rejects_symlink()
        self.assertIn("staged index (object mode 120000)", result.stderr)

    def test_base_cli_checks_staged_rename_destination(self) -> None:
        destination = "ledger/goals/GOAL-RENAMED-002.yaml"
        self.git(
            "mv", "ledger/goals/GOAL-BASE-001.yaml", destination
        )

        with mock.patch.object(hygiene, "REPO", str(self.root)):
            self.assertIn(destination, hygiene.touched_files("base-tree"))
        result = self._run_base_cli()
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertIn("GOAL-RENAMED-002", result.stderr)
        self.assertIn("new legacy GOAL identifiers", result.stderr)

    def test_base_cli_checks_staged_index_after_worktree_diverges(self) -> None:
        target = self.external_root / "index-only-target.yaml"
        target.write_text(
            self._goal_document("GOAL-INDEX-a1b2c3"), encoding="utf-8"
        )
        path = self.root / "ledger/goals/GOAL-INDEX-a1b2c3.yaml"
        path.symlink_to(target)
        self.git("add", str(path.relative_to(self.root)))
        path.unlink()
        path.write_text(
            self._goal_document("GOAL-INDEX-a1b2c3"), encoding="utf-8"
        )

        result = self._assert_base_cli_rejects_symlink()
        self.assertIn("staged index (object mode 120000)", result.stderr)

    def test_base_cli_checks_tracked_unstaged_worktree_symlink(self) -> None:
        target = self.external_root / "unstaged-target.yaml"
        target.write_text(
            self._goal_document("GOAL-BASE-001"), encoding="utf-8"
        )
        path = self.root / "ledger/goals/GOAL-BASE-001.yaml"
        path.unlink()
        path.symlink_to(target)

        result = self._assert_base_cli_rejects_symlink()
        self.assertIn("tracked goal path traverses symlink", result.stderr)
        self.assertNotIn("staged index", result.stderr)

    def test_base_cli_rejects_committed_goal_symlink(self) -> None:
        target = self.external_root / "committed-target.yaml"
        target.write_text(
            self._goal_document("GOAL-COMMITTED-a1b2c3"), encoding="utf-8"
        )
        path = self.root / "ledger/goals/GOAL-COMMITTED-a1b2c3.yaml"
        path.symlink_to(target)
        self.git("add", str(path.relative_to(self.root)))
        self.git("commit", "-qm", "commit goal symlink")

        result = self._assert_base_cli_rejects_symlink()
        self.assertIn("staged index (object mode 120000)", result.stderr)

    def test_base_cli_allows_ordinary_staged_random_goal(self) -> None:
        self._write_goal("GOAL-ORDINARY-deadbe", sharded=True)
        self.git("add", "ledger/goals/GOAL-ORDINARY-deadbe/goal.yaml")

        result = self._run_base_cli()
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        self.assertNotIn("symlinked goal paths", result.stderr)

    def test_base_cli_does_not_mislabel_out_of_scope_symlink(self) -> None:
        target = self.external_root / "ordinary-target.txt"
        target.write_text("ordinary fixture\n", encoding="utf-8")
        link = self.root / "misc/fixture-link"
        link.parent.mkdir()
        link.symlink_to(target)
        self.git("add", str(link.relative_to(self.root)))

        result = self._run_base_cli()
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        self.assertNotIn("symlinked goal paths", result.stderr)

    def test_base_cli_ignores_untracked_goal_until_staged(self) -> None:
        target = self.external_root / "untracked-target.yaml"
        target.write_text(
            self._goal_document("GOAL-UNTRACKED-a1b2c3"), encoding="utf-8"
        )
        link = self.root / "ledger/goals/GOAL-UNTRACKED-a1b2c3.yaml"
        link.symlink_to(target)

        untracked = self._run_base_cli()
        self.assertEqual(
            untracked.returncode, 0, (untracked.stdout, untracked.stderr)
        )
        self.assertNotIn("symlinked goal paths", untracked.stderr)

        self.git("add", str(link.relative_to(self.root)))
        staged = self._assert_base_cli_rejects_symlink()
        self.assertIn("staged index (object mode 120000)", staged.stderr)

    def test_ordinary_sharded_directory_remains_valid(self) -> None:
        goal_id = "GOAL-ORDINARY-a1b2c3"
        path = self.root / "ledger/goals" / goal_id / "goal.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(self._goal_document(goal_id), encoding="utf-8")
        self.git("add", str(path.relative_to(self.root)))

        self.assertEqual(self._symlink_problems(), [])
        context = self._validator_context()
        self.assertIn(goal_id, context.ids)
        self.assertFalse(any("symlink" in error for error in context.errors),
                         context.errors)


if __name__ == "__main__":
    unittest.main()
