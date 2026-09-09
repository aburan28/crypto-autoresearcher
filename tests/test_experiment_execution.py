"""Offline regression tests. Real subprocesses; simulated dispatcher transport.

The real repository dispatcher/archive verifier remains unchanged. These tests
exercise the adapter's contract with its emitted plan, not a live campaign.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import experiment_execution as execution
import newest_experiments as selector

DRIVER = '''import json, pathlib, sys, time
mode, target = sys.argv[1:3]
p = pathlib.Path(target)
if mode == "check":
    data = json.loads((p / "raw-result.json").read_text())
    assert (p / "manifest.yaml").is_file()
    sys.exit(1 if data.get("bad") else 0)
kind = sys.argv[3]
if kind == "fail":
    print("simulated infrastructure failure", file=sys.stderr)
    sys.exit(4)
if kind == "sleep":
    time.sleep(30)
if kind != "missing":
    (p / "raw-result.json").write_text(json.dumps({"effect": -1, "bad": kind == "bad"}))
(p / "manifest.yaml").write_text("status: observed\\n")
print("measured negative observation")
'''
DISPATCHER = '''import argparse, json
p=argparse.ArgumentParser()
p.add_argument("queue")
for arg in ("output", "report", "repo-root", "claims", "now"):
    p.add_argument("--"+arg)
a=p.parse_args()
assert a.claims == "refs" and a.now
q=json.load(open(a.queue))
json.dump(q["test_dispatch_plan"], open(a.output,"w"))
open(a.report,"w").write("fixture, not a real archive verification")
'''


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.exp = "EXP-ECDLP-aabbcc"
        self.expdir = self.root / "experiments" / self.exp
        self.expdir.mkdir(parents=True)
        (self.root / "tools").mkdir()
        (self.root / "tools/research_dispatch.py").write_text(DISPATCHER)
        (self.root / "driver.py").write_text(DRIVER)
        self.specpath = self.expdir / "specification.yaml"
        self.spec = {"id": self.exp, "status": "approved", "approved_by": "DEC-20260909-aabbcc",
                     "frozen": True, "designed_at": "2026-09-09", "goal_id": "GOAL-ECDLP-aabbcc"}
        self.specpath.write_text(json.dumps(self.spec))  # JSON is valid YAML
        self.queuepath = self.root / "coordination/dispatch_queue.json"
        self.queuepath.parent.mkdir()
        self.path = self.expdir / "trial-plan.json"
        self.plan = {"schema": execution.PLAN_SCHEMA, "experiment_id": self.exp,
                     "task_id": "TASK-20260909-aabbcc", "frozen": True,
                     "approved_by": self.spec["approved_by"],
                     "specification": self.specpath.relative_to(self.root).as_posix(),
                     "specification_sha256": execution.sha256(self.specpath),
                     "queue": self.queuepath.relative_to(self.root).as_posix(),
                     "source_sha256": {"driver.py": execution.sha256(self.root / "driver.py")},
                     "trials": [self.trial(1), self.trial(2)]}
        self.expires = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        claims = self.queuepath.parent / "claims"
        claims.mkdir()
        (claims / f"{self.plan['task_id']}.1.claim.json").write_text(json.dumps({
            "owner": "test-owner", "epoch": 1, "expires_at": self.expires}))
        self.write_plan_queue()
        self.git("init", "-q")
        self.git("config", "user.name", "Execution tests")
        self.git("config", "user.email", "test@example.invalid")
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL).decode().strip()

    def commit(self):
        self.git("add", "--", ".")
        self.git("commit", "-qm", "fixture", "--allow-empty")
        self.git("update-ref", "refs/remotes/origin/test", "HEAD")

    def trial(self, index, mode="ok"):
        return {"id": f"seed-{index}", "run_id": f"RUN-ECDLP-{index:06x}",
                "argv": [sys.executable, "-S", "driver.py", "measure", "{run_dir}", mode],
                "check_argv": [sys.executable, "-S", "driver.py", "check", "{run_dir}"],
                "memory_mb": 256, "watchdog_seconds": 5,
                "watchdog_reason": "test process protection",
                "artifacts": ["manifest.yaml", "raw-result.json"]}

    def write_plan_queue(self):
        self.path.write_text(json.dumps(self.plan))
        artifact_paths = []
        for trial in self.plan["trials"]:
            directory = execution.run_root(self.root, self.plan, trial)
            artifact_paths += [(directory / name).relative_to(self.root).as_posix()
                               for name in (*execution.GENERATED, *trial["artifacts"])]
        task = {"id": self.plan["task_id"], "role": "executor", "state": "running",
                "artifact_paths": artifact_paths,
                "claim": {"status": "live", "owner": "test-owner", "epoch": 1, "expires_at": self.expires},
                "handoff": {"budget": {"maximum_runs": None, "memory_gb": 1}, "execution": {
                    "mode": "experiments", "kind": "run", "experiment_id": self.exp,
                    "trial_plan": self.path.relative_to(self.root).as_posix(),
                    "trial_plan_sha256": execution.sha256(self.path), "approved_by": self.plan["approved_by"]}}}
        self.dispatch = {"schema": "crypto.autoresearch.dispatch_plan.v1", "gates": {"fixture": True},
                         "dispatches": [task], "plan_sha256": "f" * 64}
        self.save_dispatch()

    def save_dispatch(self):
        self.queuepath.write_text(json.dumps({"test_dispatch_plan": self.dispatch}))

    def run_plan(self):
        return execution.run_plan(self.root, self.path, "test-owner", 1)

    def authorize(self):
        return execution.authorize(self.root, self.path, self.plan, "test-owner", 1)

    def directory(self, index=0):
        return execution.run_root(self.root, self.plan, self.plan["trials"][index])

    def test_full_protocol_runs_and_does_not_rerun_negative_observations(self):
        report = self.run_plan()
        self.assertTrue(report["measurement_complete"])
        self.assertEqual(report["output_validated"], 2)
        self.assertFalse(report["publication_verified"])
        receipt = (self.directory() / "execution-receipt.json").read_bytes()
        self.run_plan()
        self.assertEqual(receipt, (self.directory() / "execution-receipt.json").read_bytes())
        self.assertEqual(json.loads((self.directory() / "raw-result.json").read_text())["effect"], -1)

    def test_empty_attempt_not_complete_not_reused_other_trial_runs(self):
        self.directory().mkdir(parents=True)
        report = self.run_plan()
        self.assertEqual(report["needs_reconciliation"], 1)
        self.assertEqual(report["output_validated"], 1)
        self.assertFalse(report["measurement_complete"])
        self.assertEqual(list(self.directory().iterdir()), [])

    def test_partial_success_resumes_remaining_trial(self):
        with execution.task_lock(self.root, self.plan["task_id"]) as fd:
            execution.execute_trial(self.root, self.path, self.plan, self.plan["trials"][0], self.authorize(), fd)
        self.assertEqual(execution.coverage(self.root, self.path)["remaining"], 1)
        self.assertTrue(self.run_plan()["measurement_complete"])

    def test_failed_trial_preserved_and_independent_trial_runs(self):
        self.plan["trials"][0] = self.trial(1, "fail")
        self.write_plan_queue(); self.commit()
        report = self.run_plan()
        self.assertEqual(report["output_validated"], 1)
        self.assertEqual(report["needs_reconciliation"], 1)
        receipt = execution.read_json(self.directory() / "execution-receipt.json")
        self.assertEqual(receipt["status"], "infrastructure_error")
        self.assertIsNone(receipt["scientific_conclusion"])
        self.run_plan()
        self.assertEqual(receipt, execution.read_json(self.directory() / "execution-receipt.json"))

    def test_failed_control_blocks_dependent_trial(self):
        self.plan["trials"][0] = self.trial(1, "fail")
        self.plan["trials"][1]["depends_on"] = ["seed-1"]
        self.write_plan_queue(); self.commit()
        report = self.run_plan()
        self.assertEqual(report["waiting_on_dependencies"], 1)
        self.assertFalse(self.directory(1).exists())

    def test_invalid_output_is_not_completion(self):
        for mode in ("bad", "missing"):
            with self.subTest(mode=mode):
                trial = self.trial(10 if mode == "bad" else 11, mode)
                self.plan["trials"] = [trial]
                self.write_plan_queue(); self.commit()
                report = self.run_plan()
                self.assertEqual(report["output_validated"], 0)
                self.assertEqual(execution.read_json(self.directory() / "execution-receipt.json")["status"], "invalid_output")

    def test_watchdog_preserves_failure_not_scientific_conclusion(self):
        self.plan["trials"] = [self.trial(1, "sleep")]
        self.plan["trials"][0]["watchdog_seconds"] = 0.15
        self.write_plan_queue(); self.commit()
        self.assertFalse(self.run_plan()["measurement_complete"])
        self.assertEqual(execution.read_json(self.directory() / "execution-receipt.json")["status"], "watchdog_expired")

    def test_artifact_tampering_requires_reconciliation(self):
        self.run_plan()
        (self.directory() / "raw-result.json").write_text('{"effect": 100}')
        report = self.run_plan()
        self.assertEqual(report["needs_reconciliation"], 1)
        self.assertEqual((self.directory() / "raw-result.json").read_text(), '{"effect": 100}')

    def test_corrupt_receipt_never_relaunches(self):
        self.directory().mkdir(parents=True)
        (self.directory() / "execution-receipt.json").write_text("not json")
        self.assertEqual(self.run_plan()["needs_reconciliation"], 1)

    def test_unauthorized_spec_refused_without_process(self):
        for field, value in (("status", "draft"), ("frozen", False), ("approved_by", None), ("execution_authorized", False)):
            with self.subTest(field=field):
                spec = {**self.spec, field: value}
                self.specpath.write_text(json.dumps(spec))
                self.plan["specification_sha256"] = execution.sha256(self.specpath)
                self.write_plan_queue(); self.commit()
                with self.assertRaises(execution.ExecutionError): self.run_plan()
                self.assertFalse(self.directory().exists())

    def test_changed_spec_hash_refused(self):
        self.specpath.write_text(self.specpath.read_text() + "\n")
        with self.assertRaisesRegex(execution.ExecutionError, "specification hash"): self.run_plan()

    def test_changed_source_refused(self):
        (self.root / "driver.py").write_text(DRIVER + "\n# changed")
        with self.assertRaisesRegex(execution.ExecutionError, "changed input"): self.run_plan()

    def test_committed_changed_source_hash_refused(self):
        (self.root / "driver.py").write_text(DRIVER + "\n# changed")
        self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "source hash"): self.run_plan()

    def test_uncommitted_queue_refused(self):
        self.queuepath.write_text(self.queuepath.read_text() + "\n")
        with self.assertRaisesRegex(execution.ExecutionError, "changed input"): self.run_plan()

    def test_unpublished_claim_refused(self):
        self.git("update-ref", "-d", "refs/remotes/origin/test")
        with self.assertRaisesRegex(execution.ExecutionError, "publish/fetch"): self.run_plan()

    def test_wrong_owner_or_epoch_refused(self):
        for owner, epoch in (("somebody-else", 1), ("test-owner", 2)):
            with self.subTest(owner=owner, epoch=epoch):
                with self.assertRaisesRegex(execution.ExecutionError, "owner/epoch"):
                    execution.run_plan(self.root, self.path, owner, epoch)

    def test_expired_claim_refused(self):
        self.dispatch["dispatches"][0]["claim"]["expires_at"] = "2020-01-01T00:00:00Z"
        self.save_dispatch(); self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "expired"): self.run_plan()

    def test_claim_rechecked_between_trials(self):
        count = 0
        def gate(*args):
            nonlocal count
            count += 1
            if count > 1: raise execution.ExecutionError("claim changed")
            return execution.authorize(*args)
        with self.assertRaisesRegex(execution.ExecutionError, "claim changed"):
            execution.run_plan(self.root, self.path, "test-owner", 1, gate=gate)
        self.assertEqual(execution.coverage(self.root, self.path)["output_validated"], 1)
        self.assertFalse(self.directory(1).exists())

    def test_non_executor_roles_refused(self):
        for role in ("idea-generator", "coordinator", "reviewer"):
            with self.subTest(role=role):
                self.dispatch["dispatches"][0]["role"] = role
                self.save_dispatch(); self.commit()
                with self.assertRaisesRegex(execution.ExecutionError, "executor"): self.run_plan()

    def test_proposal_binding_refused(self):
        self.dispatch["dispatches"][0]["handoff"]["execution"]["kind"] = "proposal"
        self.save_dispatch(); self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "execution-only"): self.run_plan()

    def test_failed_dispatch_gate_refused(self):
        self.dispatch["gates"]["fixture"] = False
        self.save_dispatch(); self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "gates failed"): self.run_plan()

    def test_zero_run_task_refused(self):
        self.dispatch["dispatches"][0]["handoff"]["budget"]["maximum_runs"] = 0
        self.save_dispatch(); self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "zero-run"): self.run_plan()

    def test_missing_archive_coverage_refused(self):
        self.dispatch["dispatches"][0]["artifact_paths"].pop()
        self.save_dispatch(); self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "archive coverage"): self.run_plan()

    def test_memory_above_handoff_refused(self):
        self.dispatch["dispatches"][0]["handoff"]["budget"]["memory_gb"] = 0.1
        self.save_dispatch(); self.commit()
        with self.assertRaisesRegex(execution.ExecutionError, "memory"): self.run_plan()

    def test_lock_rejects_second_supervisor(self):
        with execution.task_lock(self.root, self.plan["task_id"]):
            with self.assertRaisesRegex(execution.ExecutionError, "local supervisor"):
                self.run_plan()

    def test_empty_and_duplicate_plans_refused(self):
        for trials in ([], [self.trial(1), self.trial(1)]):
            self.plan["trials"] = trials
            self.path.write_text(json.dumps(self.plan))
            with self.assertRaises(execution.ExecutionError): execution.load_plan(self.root, self.path)

    def test_bad_dependencies_refused(self):
        self.plan["trials"][0]["depends_on"] = ["seed-2"]
        self.path.write_text(json.dumps(self.plan))
        with self.assertRaisesRegex(execution.ExecutionError, "earlier trials"): execution.load_plan(self.root, self.path)

    def test_shell_string_and_unbound_command_refused(self):
        for argv in ("python3 driver.py", ["python3", "unbound.py"]):
            self.plan["trials"][0]["argv"] = argv
            self.path.write_text(json.dumps(self.plan))
            with self.assertRaises(execution.ExecutionError): execution.load_plan(self.root, self.path)

    def test_bedrock_command_refused(self):
        self.plan["trials"][0]["argv"].append("--backend=Bedrock")
        self.path.write_text(json.dumps(self.plan))
        with self.assertRaisesRegex(execution.ExecutionError, "Bedrock"): execution.load_plan(self.root, self.path)

    def test_bad_memory_and_watchdog_refused(self):
        for value in (0, -1, True, float("inf"), float("nan")):
            self.plan["trials"][0]["memory_mb"] = value
            self.path.write_text(json.dumps(self.plan))
            with self.assertRaises(execution.ExecutionError): execution.load_plan(self.root, self.path)

    def test_path_traversal_refused(self):
        for path in ("../outside", "/tmp/outside", "a/../b", "a//b", "./a", "a\\b"):
            with self.subTest(path=path):
                with self.assertRaises(execution.ExecutionError): execution.safe_path(self.root, path)

    def test_symlink_plan_and_output_refused(self):
        alias = self.root / "alias.json"
        alias.symlink_to(self.path)
        with self.assertRaises(execution.ExecutionError): execution.load_plan(self.root, alias)
        runs = self.expdir / "runs"
        outside = self.root / "other"
        outside.mkdir()
        runs.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(execution.ExecutionError): self.run_plan()

    def test_read_only_status_creates_no_runs(self):
        with patch("builtins.print"):
            self.assertEqual(execution.main(["status", "--repo", str(self.root), "--plan", str(self.path)]), 0)
        self.assertFalse((self.expdir / "runs").exists())

    def test_cli_refuses_missing_claim(self):
        with patch("sys.stderr"):
            self.assertEqual(execution.main(["run", "--repo", str(self.root), "--plan", str(self.path)]), 2)
        self.assertFalse((self.expdir / "runs").exists())


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "orchestration").mkdir()
        (self.root / "orchestration/research-priority.yaml").write_text('ecc_areas: [ECDLP, DREG]\n')

    def experiment(self, ident, date="2026-09-09", **overrides):
        directory = self.root / "experiments" / ident
        directory.mkdir(parents=True)
        spec = {"id": ident, "status": "approved", "approved_by": "DEC-test", "frozen": True,
                "designed_at": date, "goal_id": "GOAL-ECDLP-aabbcc", **overrides}
        (directory / "specification.yaml").write_text(json.dumps(spec))
        return directory

    def test_ecc_first_newest_then_id_tie_break(self):
        for ident, date in (("EXP-AES-aaaaaa", "2026-09-10"), ("EXP-ECDLP-aaaaaa", "2026-09-08"),
                            ("EXP-ECDLP-bbbbbb", "2026-09-09"), ("EXP-DREG-cccccc", "2026-09-09")):
            self.experiment(ident, date)
        self.assertEqual([r["id"] for r in selector.newest_runnable(self.root)],
                         ["EXP-ECDLP-bbbbbb", "EXP-DREG-cccccc", "EXP-ECDLP-aaaaaa", "EXP-AES-aaaaaa"])

    def test_legacy_activity_visible_but_not_completed_or_blindly_rerun(self):
        directory = self.experiment("EXP-ECDLP-aaaaaa")
        (directory / "runs/RUN-ECDLP-aabbcc").mkdir(parents=True)
        self.assertFalse(selector._completed(directory))
        self.assertEqual(selector.newest_runnable(self.root), [])
        rows = selector.newest_runnable(self.root, include_blocked=True)
        self.assertEqual(rows[0]["execution_state"], "needs_reconciliation")

    def test_bare_report_not_completion(self):
        directory = self.experiment("EXP-ECDLP-aaaaaa")
        (directory / "execution_report.yaml").write_text("status: completed\n")
        self.assertFalse(selector._completed(directory))
        self.assertEqual(selector.newest_runnable(self.root, include_blocked=True)[0]["execution_state"], "needs_reconciliation")

    def test_bad_plan_visible_as_repair(self):
        directory = self.experiment("EXP-ECDLP-aaaaaa")
        (directory / "trial-plan.json").write_text("[]")
        self.assertEqual(selector.newest_runnable(self.root), [])
        self.assertEqual(selector.newest_runnable(self.root, include_blocked=True)[0]["execution_state"], "needs_plan_repair")

    def test_approval_and_supersession_filters_preserved(self):
        self.experiment("EXP-ECDLP-aaaaaa")
        self.experiment("EXP-ECDLP-bbbbbb", supersedes="EXP-ECDLP-aaaaaa")
        self.experiment("EXP-ECDLP-cccccc", execution_authorized=False)
        self.experiment("EXP-ECDLP-dddddd", frozen=False)
        self.experiment("EXP-ECDLP-eeeeee", approved_by=None)
        self.assertEqual([r["id"] for r in selector.newest_runnable(self.root)], ["EXP-ECDLP-bbbbbb"])

    def test_named_scope_never_falls_back_to_other_goal(self):
        self.experiment("EXP-ECDLP-aaaaaa")
        self.experiment("EXP-ECDLP-bbbbbb", goal_id="GOAL-OTHER-aabbcc")
        self.assertEqual(selector.newest_runnable(self.root, goal="GOAL-MISSING-aabbcc"), [])
        rows = selector.newest_runnable(self.root, experiment_ids={"EXP-ECDLP-aaaaaa"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "EXP-ECDLP-aaaaaa")

    def test_malformed_yaml_does_not_crash_selection(self):
        directory = self.experiment("EXP-ECDLP-aaaaaa")
        (directory / "specification.yaml").write_text("- not-a-mapping\n")
        self.assertEqual(selector.newest_runnable(self.root), [])


if __name__ == "__main__":
    unittest.main()
