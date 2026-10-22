"""One-trial standard-supervisor order and fail-closed admission controls.

The fixture is a disposable local Git repository. The real supervisor creates
launch.json and starts real Python driver/checker subprocesses; only the
dispatcher transport and scientific worker are synthetic. No Sage is called.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import execute
import check
import driver

DISPATCHER = '''import argparse, json
p=argparse.ArgumentParser()
p.add_argument("queue")
for arg in ("output", "report", "repo-root", "claims", "now"):
    p.add_argument("--"+arg)
a=p.parse_args()
assert a.claims == "refs" and a.now
q=json.load(open(a.queue))
json.dump(q["test_dispatch_plan"], open(a.output,"w"))
open(a.report,"w").write("synthetic dispatcher transport")
'''
WORKER = '''import argparse, json, pathlib, sys
p=argparse.ArgumentParser()
p.add_argument("mode", choices=("driver", "check"))
for key in ("plan", "owner", "epoch", "trial-id", "run-dir"):
    p.add_argument("--"+key, required=True)
a=p.parse_args()
sys.path.insert(0, str(pathlib.Path(__file__).parent / "research/icperf_prime63_inflight_admission_20261017"))
sys.path.insert(0, "__ACTUAL_TOOLS__")
import execute
root=pathlib.Path(__file__).parent
run_dir=pathlib.Path(a.run_dir)
admitted=execute.admit(pathlib.Path(a.plan), a.owner, int(a.epoch), root=root,
                       run_dir=run_dir, trial_id=a.trial_id)
assert admitted["selector_execution_state"] == "needs_reconciliation"
if a.mode == "driver":
    (run_dir / "raw-result.json").write_text(json.dumps({"fixture": "inflight", "sage_calls": 0}))
    manifest={"run":{"id":admitted["run_id"],
       "experiment_id":admitted["plan"]["experiment_id"],"status":"completed",
       "code":{"commit":admitted["authorization"]["commit"],"command":"fixture_worker.py driver"},
       "environment":{"python":"fixture"},"inputs":{"parameters":{}},
       "timing":{"wall_seconds":0},"result":{"certificate":{"kind":"none"}}}}
    (run_dir / "manifest.yaml").write_text(json.dumps(manifest))
else:
    assert json.loads((run_dir / "raw-result.json").read_text())["sage_calls"] == 0
print(json.dumps({"phase":a.mode,"inflight":admitted["selector_execution_state"],
                  "launch_sha256":admitted["launch_sha256"]}, sort_keys=True))
'''


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InflightControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fixture-", dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.exp = "EXP-PRIME63-aabbcc"
        self.task = "TASK-20261017-aabbcc"
        self.trial_id = "prime63-panel"
        self.run_id = "RUN-PRIME63-aabbcc"
        self.owner, self.epoch = "fixture-owner", 1
        self.expdir = self.root / "experiments" / self.exp
        self.expdir.mkdir(parents=True)
        (self.root / "tools").mkdir()
        (self.root / "tools/research_dispatch.py").write_text(DISPATCHER)
        self.worker_source = WORKER.replace("__ACTUAL_TOOLS__", str(REPO / "tools"))
        (self.root / "fixture_worker.py").write_text(self.worker_source)
        policy = self.root / "orchestration/research-priority.yaml"
        policy.parent.mkdir()
        shutil.copy2(REPO / "orchestration/research-priority.yaml", policy)
        required = {
            "research/icperf_prime63_inflight_admission_20261017/execute.py",
            "research/icperf_prime63_inflight_admission_20261017/driver.py",
            "research/icperf_prime63_inflight_admission_20261017/check.py",
            "research/icperf_prime63_inflight_admission_20261017/input_manifest.json",
            "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz",
            "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json",
            "research/icperf_prime63_pilot_launcher_20261017/input_replay.json",
            "research/icperf_prime63_pilot_launcher_20261017/verify_run.py",
            "research/icperf_prime_wide_backend_retry_20261017/backend.py",
            "research/icperf_prime_475_target_systems_20261017/systems.json.gz",
        }
        for relative in required:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if relative.startswith("research/icperf_prime63_inflight_admission") and (REPO / relative).exists():
                shutil.copy2(REPO / relative, target)
            else:
                target.write_text("synthetic source closure fixture\n")
        self.spec = self.expdir / "specification.yaml"
        self.spec.write_text(json.dumps({"id": self.exp, "status": "approved",
            "approved_by": "DEC-20261017-aabbcc", "frozen": True,
            "goal_id": "GOAL-ICPERF-e6b6a4", "designed_at": "2026-10-17"}))
        self.queue = self.root / "coordination/dispatch_queue.json"
        self.queue.parent.mkdir()
        self.plan_path = self.expdir / "trial-plan.json"
        self.run_dir = self.expdir / "runs" / self.run_id
        argv = [sys.executable, "fixture_worker.py", "driver", "--plan", str(self.plan_path),
                "--owner", self.owner, "--epoch", "1", "--trial-id", self.trial_id,
                "--run-dir", "{run_dir}"]
        checker = argv.copy()
        checker[2] = "check"
        self.trial = {"id": self.trial_id, "run_id": self.run_id,
            "argv": argv, "check_argv": checker, "memory_mb": 512,
            "watchdog_seconds": 30, "watchdog_reason": "bounded engineering fixture",
            "artifacts": ["manifest.yaml", "raw-result.json"]}
        sources = {name: digest(self.root / name) for name in required}
        sources["fixture_worker.py"] = digest(self.root / "fixture_worker.py")
        self.plan = {"schema": execute.execution.PLAN_SCHEMA, "frozen": True,
            "experiment_id": self.exp, "task_id": self.task,
            "approved_by": "DEC-20261017-aabbcc",
            "specification": self.spec.relative_to(self.root).as_posix(),
            "specification_sha256": digest(self.spec),
            "queue": self.queue.relative_to(self.root).as_posix(),
            "source_sha256": sources, "trials": [self.trial]}
        self.plan_path.write_text(json.dumps(self.plan, sort_keys=True))
        expires = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        self.claim = self.queue.parent / "claims" / f"{self.task}.1.claim.json"
        self.claim.parent.mkdir()
        self.claim.write_text(json.dumps({"owner": self.owner, "epoch": 1,
                                          "expires_at": expires}))
        execution_binding = {"mode": "experiments", "kind": "run",
            "experiment_id": self.exp,
            "trial_plan": self.plan_path.relative_to(self.root).as_posix(),
            "trial_plan_sha256": digest(self.plan_path),
            "approved_by": self.plan["approved_by"]}
        artifacts = [(self.run_dir / name).relative_to(self.root).as_posix()
                     for name in (*execute.execution.GENERATED, *self.trial["artifacts"])]
        task = {"id": self.task, "role": "executor", "state": "running",
            "artifact_paths": artifacts,
            "claim": {"status": "live", "owner": self.owner, "epoch": 1,
                      "expires_at": expires},
            "handoff": {"budget": {"memory_gb": 1, "maximum_runs": 1},
                        "execution": execution_binding}}
        dispatch = {"schema": "crypto.autoresearch.dispatch_plan.v1",
                    "gates": {"fixture": True}, "dispatches": [task],
                    "plan_sha256": "f"*64}
        self.queue.write_text(json.dumps({"schema": "crypto.autoresearch.dispatch_queue.v1",
            "tasks": [task], "test_dispatch_plan": dispatch}, sort_keys=True))
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "gc.auto", "0")
        self.git("config", "maintenance.auto", "false")
        self.git("add", "--", ".")
        self.git("commit", "-qm", "frozen synthetic fixture")
        self.git("update-ref", "refs/remotes/origin/fixture", "HEAD")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args],
                                       stderr=subprocess.DEVNULL).decode().strip()

    def authority(self):
        return execute.execution.authorize(self.root, self.plan_path,
                                            self.plan, self.owner, self.epoch)

    def make_launch(self, *, changed=None):
        self.run_dir.mkdir(parents=True, exist_ok=True)
        data = {"plan_sha256": digest(self.plan_path), "trial_id": self.trial_id,
                "run_id": self.run_id, "started_at": datetime.now(timezone.utc).isoformat(),
                "authority": self.authority(), "argv": [a.replace("{run_dir}", str(self.run_dir))
                    for a in self.trial["argv"]],
                "check_argv": [a.replace("{run_dir}", str(self.run_dir))
                    for a in self.trial["check_argv"]], "supervisor_pid": os.getpid()}
        if changed:
            changed(data)
        (self.run_dir / "launch.json").write_text(json.dumps(data))

    def test_real_supervisor_order_parent_and_child(self):
        with patch.object(execute.newest_experiments, "validate_queue", return_value=None):
            before = execute.admit(self.plan_path, self.owner, self.epoch, root=self.root)
        self.assertEqual(before["selector_execution_state"], "ready")
        report = execute.execution.run_plan(self.root, self.plan_path,
                                            self.owner, self.epoch)
        self.assertTrue(report["measurement_complete"])
        self.assertEqual(report["output_validated"], 1)
        self.assertIn('"inflight": "needs_reconciliation"',
                      (self.run_dir / "stdout.log").read_text())
        self.assertIn('"inflight": "needs_reconciliation"',
                      (self.run_dir / "check.stdout.log").read_text())
        self.assertEqual(json.loads((self.run_dir / "raw-result.json").read_text())["sage_calls"], 0)
        receipt = json.loads((self.run_dir / "execution-receipt.json").read_text())
        self.assertEqual((receipt["status"], receipt["returncode"],
                          receipt["check_returncode"]), ("output_validated", 0, 0))
        with self.assertRaisesRegex(execute.execution.ExecutionError, "prior attempt"):
            execute.admit(self.plan_path, self.owner, self.epoch, root=self.root,
                          run_dir=self.run_dir, trial_id=self.trial_id)
        print(json.dumps({"control": "real_one_trial_supervisor_order",
            "pre_dispatch": "ready", "inside_driver": "needs_reconciliation",
            "inside_checker": "needs_reconciliation", "validated_trials": 1,
            "sage_calls": 0, "second_attempt": "refused",
            "supervisor_receipt": {"status": receipt["status"],
                "returncode": receipt["returncode"],
                "check_returncode": receipt["check_returncode"],
                "plan_sha256": receipt["plan_sha256"],
                "trial_id": receipt["trial_id"], "run_id": receipt["run_id"],
                "artifact_sha256": receipt["artifact_sha256"]},
            "launch_sha256": digest(self.run_dir / "launch.json"),
            "driver_stdout_sha256": digest(self.run_dir / "stdout.log"),
            "checker_stdout_sha256": digest(self.run_dir / "check.stdout.log")},
            sort_keys=True))

    def test_stale_forged_and_changed_launch_refusals(self):
        cases = {
            "wrong_plan_hash": lambda d: d.update(plan_sha256="0"*64),
            "wrong_trial_id": lambda d: d.update(trial_id="other"),
            "wrong_run_id": lambda d: d.update(run_id="RUN-PRIME63-dead00"),
            "wrong_owner": lambda d: d["authority"].update(owner="forged"),
            "wrong_epoch": lambda d: d["authority"].update(epoch=2),
            "wrong_argv_plan": lambda d: d["argv"].__setitem__(4, "/tmp/other-plan.json"),
            "stale_started_at": lambda d: d.update(started_at="2020-01-01T00:00:00+00:00"),
        }
        for name, change in cases.items():
            with self.subTest(name=name):
                self.make_launch(changed=change)
                with self.assertRaises((execute.execution.ExecutionError, ValueError)):
                    execute.admit(self.plan_path, self.owner, self.epoch, root=self.root,
                                  run_dir=self.run_dir, trial_id=self.trial_id)
                self.assertFalse((self.run_dir / "raw-result.json").exists())
                self.assertFalse((self.run_dir / "panel").exists())
                (self.run_dir / "launch.json").unlink()
                self.run_dir.rmdir()
        print(json.dumps({"control": "launch_refusals", "cases": len(cases),
                          "additional_output": False, "sage_calls": 0}, sort_keys=True))

    def test_source_claim_selector_and_second_attempt_refusals(self):
        self.make_launch()
        with self.assertRaisesRegex(execute.execution.ExecutionError, "wrong owner"):
            execute.admit(self.plan_path, "other-owner", self.epoch, root=self.root,
                          run_dir=self.run_dir, trial_id=self.trial_id)
        with self.assertRaisesRegex(execute.execution.ExecutionError, "wrong owner"):
            execute.admit(self.plan_path, self.owner, 2, root=self.root,
                          run_dir=self.run_dir, trial_id=self.trial_id)
        source = self.root / "fixture_worker.py"
        source.write_text(source.read_text() + "# changed\n")
        with self.assertRaisesRegex(execute.execution.ExecutionError,
                                    "uncommitted or changed input|source hash changed"):
            execute.admit(self.plan_path, self.owner, self.epoch, root=self.root,
                          run_dir=self.run_dir, trial_id=self.trial_id)
        source.write_text(self.worker_source)
        (self.run_dir / "execution-receipt.json").write_text("{}")
        with self.assertRaisesRegex(execute.execution.ExecutionError, "prior attempt"):
            execute.admit(self.plan_path, self.owner, self.epoch, root=self.root,
                          run_dir=self.run_dir, trial_id=self.trial_id)
        self.assertFalse((self.run_dir / "raw-result.json").exists())
        print(json.dumps({"control": "source_claim_second_attempt_refusals",
                          "additional_output": False, "sage_calls": 0}, sort_keys=True))

    def test_review_required_and_missing_or_expired_claim_refuse(self):
        with patch.object(execute.newest_experiments, "newest_runnable", return_value=[]):
            with self.assertRaisesRegex(execute.execution.ExecutionError,
                                        "selector is not ready"):
                execute.admit(self.plan_path, self.owner, self.epoch, root=self.root)
        self.assertFalse(self.run_dir.exists())
        self.claim.unlink()
        with self.assertRaises((execute.execution.ExecutionError, FileNotFoundError)):
            execute.admit(self.plan_path, self.owner, self.epoch, root=self.root)
        self.claim.write_text(json.dumps({"owner": self.owner, "epoch": 1,
                                          "expires_at": "2020-01-01T00:00:00+00:00"}))
        queue = json.loads(self.queue.read_text())
        queue["tasks"][0]["claim"]["expires_at"] = "2020-01-01T00:00:00+00:00"
        queue["test_dispatch_plan"]["dispatches"][0]["claim"]["expires_at"] = "2020-01-01T00:00:00+00:00"
        self.queue.write_text(json.dumps(queue, sort_keys=True))
        self.git("add", "--", ".")
        self.git("commit", "-qm", "published expired-claim control")
        self.git("update-ref", "refs/remotes/origin/fixture", "HEAD")
        with self.assertRaisesRegex(execute.execution.ExecutionError,
                                    "claim is expired|missing live claim"):
            execute.admit(self.plan_path, self.owner, self.epoch, root=self.root)
        self.assertFalse(self.run_dir.exists())
        print(json.dumps({"control": "review_required_missing_expired_claim",
                          "additional_output": False, "sage_calls": 0}, sort_keys=True))

    def test_relative_plan_token_bound_and_changed_token_refused(self):
        relative = self.plan_path.relative_to(self.root).as_posix()
        for command in (self.trial["argv"], self.trial["check_argv"]):
            command[command.index("--plan") + 1] = relative
        self.plan_path.write_text(json.dumps(self.plan, sort_keys=True))
        queue = json.loads(self.queue.read_text())
        bound = digest(self.plan_path)
        queue["tasks"][0]["handoff"]["execution"]["trial_plan_sha256"] = bound
        queue["test_dispatch_plan"]["dispatches"][0]["handoff"]["execution"]["trial_plan_sha256"] = bound
        self.queue.write_text(json.dumps(queue, sort_keys=True))
        self.git("add", "--", ".")
        self.git("commit", "-qm", "relative-plan-token control")
        self.git("update-ref", "refs/remotes/origin/fixture", "HEAD")
        self.make_launch()
        accepted = execute.admit(self.plan_path, self.owner, self.epoch,
                                 root=self.root, run_dir=self.run_dir,
                                 trial_id=self.trial_id)
        self.assertEqual(accepted["trial_id"], self.trial_id)
        launch_path = self.run_dir / "launch.json"
        launch = json.loads(launch_path.read_text())
        launch["argv"][launch["argv"].index("--plan") + 1] = "experiments/other/trial-plan.json"
        launch_path.write_text(json.dumps(launch))
        with self.assertRaisesRegex(execute.execution.ExecutionError,
                                    "launch does not bind"):
            execute.admit(self.plan_path, self.owner, self.epoch,
                          root=self.root, run_dir=self.run_dir,
                          trial_id=self.trial_id)
        print(json.dumps({"control": "relative_plan_token",
                          "relative_accepted": True, "changed_token_refused": True}, sort_keys=True))

    def panel_fixture(self, response: dict):
        self.make_launch()
        launch_sha = digest(self.run_dir / "launch.json")
        panel = self.run_dir / "panel"
        response_path = panel / "control-0/response.json"
        response_path.parent.mkdir(parents=True)
        response_path.write_text(json.dumps(response, sort_keys=True) + "\n")
        cell = {"cell": "control-0", "attempted": True,
                "status": response["status"], "response_sha256": digest(response_path)}
        cells = [cell] + [{"cell": f"natural-{i}", "attempted": False,
                           "reason": "panel_wall_censored"} for i in range(26)]
        with tarfile.open(panel / "raw.tar.gz", "w:gz") as tar:
            tar.add(response_path, arcname="control-0/response.json")
        raw_files = [{"path": "control-0/response.json", "bytes": response_path.stat().st_size,
                      "sha256": digest(response_path)}]
        receipt = {"cells": cells, "attempted": 1, "unattempted": 26,
                   "plan_sha256": digest(self.plan_path), "launch_sha256": launch_sha,
                   "run_id": self.run_id, "trial_id": self.trial_id,
                   "raw_files": raw_files, "raw_tar_sha256": digest(panel / "raw.tar.gz")}
        (panel / "receipt.json").write_text(json.dumps(receipt, sort_keys=True))
        shutil.copy2(panel / "raw.tar.gz", self.run_dir / "raw.tar.gz")
        raw = {"cells": cells, "attempted": 1, "unattempted": 26,
               "plan_sha256": digest(self.plan_path), "launch_sha256": launch_sha,
               "run_id": self.run_id, "trial_id": self.trial_id,
               "panel_receipt_sha256": digest(panel / "receipt.json"),
               "raw_archive_sha256": digest(self.run_dir / "raw.tar.gz")}
        (self.run_dir / "raw-result.json").write_text(json.dumps(raw, sort_keys=True))
        (self.run_dir / "manifest.yaml").write_text(json.dumps({"run": {"id": self.run_id}}))
        equation = [[{"coefficient": "1", "powers": [[0, 1]]},
                     {"coefficient": "-3", "powers": []}],
                    [{"coefficient": "1", "powers": [[1, 1]]},
                     {"coefficient": "-3", "powers": []}]]
        system = {"curve": {"p": "101", "a": "2", "b": "3"},
                  "variables": ["x1", "x2"], "equations": equation,
                  "m": 2, "arm": "random", "base_points": [["3", "6"]],
                  "target_point": ["30", "55"]}
        rows = [{"id": "control-0", "kind": "positive", "request": system}]
        rows += [{"id": f"natural-{i}", "kind": "natural", "request": system}
                 for i in range(26)]
        witnesses = self.root / "witnesses"
        witnesses.mkdir()
        (witnesses / "planted_witnesses.json").write_text(json.dumps({"witnesses": [
            {"cell": "control-0", "root": {"x1": "3", "x2": "3"}}]}))
        return panel, rows, witnesses

    def test_censored_positive_and_forged_ok(self):
        panel, rows, witnesses = self.panel_fixture(
            {"status": "model_cap_censored", "roots": [], "variety_called": False})
        with patch.object(execute, "OLD", witnesses):
            outcome = check.verify(self.run_dir, self.plan_path, self.owner,
                                   self.epoch, self.trial_id, root=self.root, rows=rows)
        self.assertEqual(outcome["positive_controls_censored"], 1)
        self.assertEqual(outcome["positive_controls_verified"], 0)
        self.assertEqual(outcome["positive_control_status"], "censored")
        response_path = panel / "control-0/response.json"
        response_path.unlink()
        response_path.parent.rmdir()
        with patch.object(execute, "OLD", witnesses):
            self.assertEqual(check.verify(self.run_dir, self.plan_path, self.owner,
                self.epoch, self.trial_id, root=self.root, rows=rows), outcome)
        # A separately formed forged-ok response carries complete raw hashes,
        # yet the independent planted witness check must reject it.
        bad = {"status": "ok", "root_count": 0, "roots": []}
        bad_bytes = (json.dumps(bad, sort_keys=True) + "\n").encode()
        response_path.parent.mkdir()
        response_path.write_bytes(bad_bytes)
        with tarfile.open(panel / "raw.tar.gz", "w:gz") as tar:
            tar.add(response_path, arcname="control-0/response.json")
        receipt = json.loads((panel / "receipt.json").read_text())
        receipt["cells"][0]["status"] = "ok"
        receipt["cells"][0]["response_sha256"] = digest(response_path)
        receipt["raw_files"][0]["bytes"] = len(bad_bytes)
        receipt["raw_files"][0]["sha256"] = digest(response_path)
        receipt["raw_tar_sha256"] = digest(panel / "raw.tar.gz")
        (panel / "receipt.json").write_text(json.dumps(receipt, sort_keys=True))
        shutil.copy2(panel / "raw.tar.gz", self.run_dir / "raw.tar.gz")
        raw = json.loads((self.run_dir / "raw-result.json").read_text())
        raw["cells"][0]["status"] = "ok"
        raw["cells"][0]["response_sha256"] = digest(response_path)
        raw["panel_receipt_sha256"] = digest(panel / "receipt.json")
        raw["raw_archive_sha256"] = digest(self.run_dir / "raw.tar.gz")
        (self.run_dir / "raw-result.json").write_text(json.dumps(raw, sort_keys=True))
        with patch.object(execute, "OLD", witnesses):
            with self.assertRaisesRegex(ValueError, "planted control witness missing"):
                check.verify(self.run_dir, self.plan_path, self.owner,
                             self.epoch, self.trial_id, root=self.root, rows=rows)
        print(json.dumps({"control": "censored_positive_vs_forged_ok",
                          "censored_accepted": True, "tar_only_replay": True,
                          "forged_ok_rejected": True, "sage_calls": 0}, sort_keys=True))


class ExactCheckerControls(unittest.TestCase):
    def test_driver_emits_schema_valid_manifest_without_solver(self):
        with tempfile.TemporaryDirectory(prefix="manifest-", dir=HERE) as tmp:
            run_dir = Path(tmp)
            for name in ("command.txt", "environment.json", "stdout.log", "stderr.log"):
                (run_dir / name).write_text("fixture\n")
            trial = {"id": "prime63-panel", "argv": ["python3", "driver.py"]}
            authority = {"plan": {"experiment_id": "EXP-PRIME63-aabbcc",
                                  "source_sha256": {"driver.py": "0"*64},
                                  "trials": [trial]},
                         "run_id": "RUN-PRIME63-aabbcc", "plan_sha256": "1"*64,
                         "launch_sha256": "2"*64,
                         "authorization": {"commit": "3"*40}}
            def fake_panel(*_args):
                panel = run_dir / "panel"
                panel.mkdir()
                with tarfile.open(panel / "raw.tar.gz", "w:gz"):
                    pass
                (panel / "receipt.json").write_text('{"fixture":true}\n')
                return {"attempted": 0, "unattempted": 27,
                        "cells": [], "wall_seconds": 0.0}
            with patch.object(execute, "admit", return_value=authority), \
                 patch.object(execute, "create_panel", side_effect=fake_panel):
                driver.run(Path("synthetic-plan.json"), "fixture-owner", 1,
                           "prime63-panel", run_dir)
            self.assertEqual(execute.execution.manifest_schema_errors(
                run_dir / "manifest.yaml"), [])
            self.assertEqual(json.loads((run_dir / "manifest.yaml").read_text())
                             ["run"]["result"]["certificate"]["kind"], "none")
        print(json.dumps({"control": "schema_valid_driver_manifest",
                          "sage_calls": 0}, sort_keys=True))

    def test_complete_raw_archive_detects_changed_bytes(self):
        with tempfile.TemporaryDirectory(prefix="archive-", dir=HERE) as tmp:
            panel = Path(tmp)
            raw = panel / "cell/request.json"
            raw.parent.mkdir()
            raw.write_text('{"p":"101"}\n')
            entry = {"path": "cell/request.json", "bytes": raw.stat().st_size,
                     "sha256": digest(raw)}
            with tarfile.open(panel / "raw.tar.gz", "w:gz") as tar:
                tar.add(raw, arcname=entry["path"])
            receipt = {"raw_files": [entry], "raw_tar_sha256": digest(panel / "raw.tar.gz")}
            self.assertEqual(check.verify_archive(panel, receipt)[entry["path"]], raw.read_bytes())
            raw.write_text('{"p":"103"}\n')
            with self.assertRaisesRegex(ValueError, "disk and archived raw bytes mismatch"):
                check.verify_archive(panel, receipt)
            raw.unlink()
            raw.parent.rmdir()
            self.assertEqual(check.verify_archive(panel, receipt)[entry["path"]], b'{"p":"101"}\n')
        print(json.dumps({"control": "raw_archive_byte_coverage",
                          "valid": 1, "altered_rejected": 1, "tar_only_replay": True}, sort_keys=True))

    def test_small_prime_polynomial_membership_sign_and_full_point(self):
        equation1 = [{"coefficient": "1", "powers": [[0, 1]]},
                     {"coefficient": "-3", "powers": []}]
        equation2 = [{"coefficient": "1", "powers": [[1, 1]]},
                     {"coefficient": "-3", "powers": []}]
        system = {"curve": {"p": "101", "a": "2", "b": "3"},
                  "variables": ["x1", "x2"], "equations": [equation1, equation2],
                  "m": 2, "arm": "random", "base_points": [["3", "6"]],
                  "target_point": ["30", "55"]}
        root = {"variables": {"x1": "3", "x2": "3"}, "ys": ["6", "6"]}
        check.verify_root(system, root)
        altered = json.loads(json.dumps(system))
        altered["equations"][0][1]["coefficient"] = "-4"
        with self.assertRaisesRegex(ValueError, "polynomial"):
            check.verify_root(altered, root)
        altered = json.loads(json.dumps(system))
        altered["base_points"] = [["30", "55"]]
        with self.assertRaisesRegex(ValueError, "base membership"):
            check.verify_root(altered, root)
        altered = json.loads(json.dumps(system))
        altered["target_point"] = ["3", "6"]
        with self.assertRaisesRegex(ValueError, "full target"):
            check.verify_root(altered, root)
        wrong_sign = json.loads(json.dumps(root))
        wrong_sign["ys"] = ["95", "95"]
        with self.assertRaisesRegex(ValueError, "full target"):
            check.verify_root(system, wrong_sign)
        rounded = json.loads(json.dumps(root))
        rounded["variables"]["x1"] = 3.0
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            check.verify_root(system, rounded)
        print(json.dumps({"control": "independent_exact_checker",
                          "small_prime": 101, "valid": 1, "altered_rejected": 5,
                          "sage_calls": 0}, sort_keys=True))

    def test_frozen_schedule_and_protection_constants(self):
        import importlib.util
        old = REPO / "research/icperf_prime63_pilot_launcher_20261017/execute.py"
        spec = importlib.util.spec_from_file_location("frozen_prime63_launcher", old)
        frozen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frozen)
        current, archived = execute.schedule(), frozen.schedule()
        self.assertEqual(len(current), 27)
        self.assertEqual(json.dumps(current, sort_keys=True),
                         json.dumps(archived, sort_keys=True))
        self.assertEqual((execute.CALL_SECONDS, execute.RSS_CAP, execute.SCRATCH_CAP,
                          execute.MODEL_CAP, execute.PANEL_SECONDS),
                         (300, 8*1024**3, 8*1024**3, 64, 4*3600))
        self.assertEqual(digest(old),
            "8fb47e68209947d5d6a7490cafde5921c2b2156c10cf9d97b961f4e555598854")
        self.assertEqual(digest(REPO / "research/icperf_prime63_admission_fix_20261017/execute.py"),
            "2acea9de53c7b1e8f4d5ca6f913652f9d43cb6c0a52ae34851f05fec67ca91cb")
        print(json.dumps({"control": "frozen_27_schedule_and_sources",
                          "cells": 27, "identical": True, "old_hashes_match": True},
                         sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
