"""Scope regressions exercise real Git histories, including renames and >300 files."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("ci_scope", Path(__file__).with_name("ci_scope.py"))
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)


class ScopeTests(unittest.TestCase):
    def test_docs_only_skip_software_gates(self):
        gates = scope.classify(["README.md", "docs/ci.md", "papers/draft/main.tex"])
        self.assertFalse(any(gates.values()))

    def test_records_keep_integrity_but_skip_software_regressions(self):
        for path in ("ledger/goals/GOAL-X.yaml", "experiments/EXP-X/runs/RUN-X/manifest.yaml",
                     "knowledge/techniques/KN-TECH-X.md", "coordination/dispatch_queue.json"):
            with self.subTest(path=path):
                gates = scope.classify([path])
                self.assertTrue(gates["ledger"] and gates["static"] and gates["full_checkout"])
                self.assertFalse(gates["tests"] or gates["runtime"])

    def test_static_corpus_checks_follow_their_inputs(self):
        goal = scope.classify(["ledger/goals/GOAL-X.yaml"])
        self.assertTrue(goal["frontier"])
        self.assertFalse(goal["knowledge_index"] or goal["source_index"] or goal["autolab"])
        literature = scope.classify(["knowledge/literature/KN-LIT-X.md"])
        self.assertTrue(literature["knowledge_index"] and literature["source_index"])
        run = scope.classify(["experiments/EXP-X/runs/RUN-X/manifest.yaml"])
        self.assertTrue(run["autolab"])
        self.assertFalse(run["source_index"])
        self.assertTrue(scope.classify(["inputs/source/source_record.yaml"])["source_index"])

    def test_claims_run_fidelity(self):
        self.assertTrue(scope.classify(["claims/paired.json"])["progress"])

    def test_code_dependencies_instructions_workflows_unknown_are_conservative(self):
        for path in ("src/crypto_autoresearcher/gf2/_kernels.c", "orchestration/agent/runtime.py",
                     "tests/test_agent_runtime.py", "pyproject.toml", "requirements-agent.txt",
                     "uv.lock", "AGENTS.md", ".claude/skills/pr/SKILL.md",
                     ".github/workflows/validate.yml", ".github/scripts/ci_scope.py",
                     "experiments/EXP-X/implementation/main.py", "new-root/file.json",
                     "docs/new-configuration.json"):
            with self.subTest(path=path):
                self.assertTrue(all(scope.classify([path]).values()))

    def test_forced_scheduled_or_manual_checks_run_every_gate(self):
        self.assertTrue(all(scope.classify([], force=True).values()))
        self.assertEqual(scope.resolve_base({}, "workflow_dispatch"), (None, True))
        self.assertEqual(scope.resolve_base({}, "schedule"), (None, True))
        self.assertEqual(scope.resolve_base({"before": "0" * 40}, "push"), (None, True))

    def test_real_diff_rename_deletion_and_more_than_300_files(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            def git(*args):
                return subprocess.run(["git", *args], cwd=repo, check=True,
                                      capture_output=True, text=True).stdout.strip()
            git("init", "-q", "-b", "main")
            git("config", "user.email", "ci@example.invalid")
            git("config", "user.name", "CI fixture")
            (repo / "src").mkdir()
            (repo / "src/runtime.py").write_text("x = 1\n")
            (repo / "src/keep.txt").write_text("keep this directory\n")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            (repo / "docs").mkdir()
            git("mv", "src/runtime.py", "docs/runtime.md")
            for index in range(350):
                (repo / f"docs/{index:03d}.md").write_text("documentation\n")
            (repo / "docs/spaces and\nnewline.md").write_text("unusual name\n")
            git("add", ".")
            git("commit", "-qm", "rename and documentation")
            old_cwd = os.getcwd()
            try:
                os.chdir(repo)
                paths = scope.changed_paths(base)
                self.assertIn("src/runtime.py", paths)
                self.assertIn("docs/runtime.md", paths)
                self.assertIn("docs/spaces and\nnewline.md", paths)
                self.assertGreater(len(paths), 300)
                self.assertTrue(all(scope.classify(paths).values()))
                with self.assertRaises(subprocess.CalledProcessError):
                    scope.changed_paths("missing-base")
                # A real merge commit has the current base as its first parent.
                git("checkout", "-qb", "feature", base)
                (repo / "src/feature.py").write_text("feature = True\n")
                git("add", ".")
                git("commit", "-qm", "feature")
                git("checkout", "-q", "main")
                current_base = git("rev-parse", "HEAD")
                git("merge", "--no-ff", "-m", "test merge", "feature")
                chosen, forced = scope.resolve_base({"pull_request": {"base": {"sha": base}}}, "pull_request")
                self.assertEqual(chosen, current_base)
                self.assertFalse(forced)
                self.assertEqual(scope.changed_paths(chosen), ["src/feature.py"])
                self.assertEqual(scope.resolve_base({"merge_group": {"base_sha": current_base}}, "merge_group"),
                                 (current_base, False))
            finally:
                os.chdir(old_cwd)

    def test_formal_test_only_changes_skip_mathlib_but_source_verifier_and_deps_do_not(self):
        for path in ("tests/test_lean_live.py", "tests/test_formal_targets.py",
                     "tests/test_verify_formal_targets.py", "formal/smoke/CryptoResearch/Smoke.lean",
                     "formal/README.md"):
            with self.subTest(path=path):
                self.assertFalse(scope.formal_workspace_needed([path]))
        for path in ("formal/CryptoResearch/Semaev/Symmetrization.lean", "formal/targets/target.yaml",
                     "formal/lake-manifest.json", "formal/AxiomAudit.lean",
                     "orchestration/formal/lean_worker.py", "tools/verify_formal_targets.py",
                     "tools/rebuild_formal_root.py", "pyproject.toml", "requirements-dev.txt",
                     ".github/workflows/lean-verification.yml", "unknown/file.json"):
            with self.subTest(path=path):
                self.assertTrue(scope.formal_workspace_needed([path]))
        self.assertTrue(scope.formal_workspace_needed([], force=True))

    def test_unrelated_software_and_records_do_not_build_lean(self):
        for path in ("README.md", "ui/app.js", "src/crypto_autoresearcher/gf2/_kernels.c",
                     "ledger/goals/GOAL-X.yaml", "claims/paired.json", "tests/test_ui_ops.py"):
            with self.subTest(path=path):
                self.assertEqual(scope.formal_scope([path]), (False, False))
        self.assertEqual(scope.formal_scope(["research/THM_SEMAEV_FALL1.md"]), (True, False))
        self.assertEqual(scope.formal_scope(["new-source-family/file.py"]), (True, True))

    def test_cli_fails_closed_for_missing_base_or_event(self):
        script = Path(scope.__file__)
        with tempfile.TemporaryDirectory() as temp:
            event = Path(temp) / "event.json"
            output = Path(temp) / "output"
            event.write_text(json.dumps({"before": "deadbeef"}))
            proc = subprocess.run(["python3", str(script), "--event", str(event),
                                   "--event-name", "push", "--output", str(output)],
                                  capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
