"""Admission-only negative controls and mocked forwarding for TASK-37ebda.

No test here launches a wide solver or claims a real positive authorization.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import execute


def fake_plan():
    required = {
        "research/icperf_prime63_admission_fix_20261017/execute.py",
        "research/icperf_prime63_admission_fix_20261017/input_manifest.json",
        "research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz",
        "research/icperf_prime63_pilot_launcher_20261017/planted_witnesses.json",
        "research/icperf_prime63_pilot_launcher_20261017/input_replay.json",
        "research/icperf_prime63_pilot_launcher_20261017/verify_run.py",
        "research/icperf_prime_wide_backend_retry_20261017/backend.py",
        "research/icperf_prime_475_target_systems_20261017/systems.json.gz",
    }
    return {"experiment_id": "EXP-PRIME63-abcdef", "task_id": "TASK-FUTURE-abcdef",
            "source_sha256": {name: "0" * 64 for name in sorted(required)}}


class AdmissionControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="icperf-prime63-admission-", dir=HERE)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = self.root / "experiments/EXP-PRIME63-abcdef/trial-plan.json"
        self.plan.parent.mkdir(parents=True)
        self.plan.write_text('{"mock":"plan"}\n')
        self.relative = self.plan.relative_to(self.root).as_posix()
        self.plan_sha = hashlib.sha256(self.plan.read_bytes()).hexdigest()
        self.out = self.root / "run-output"
        self.worker_output = self.root / "worker-output.json"
        self.scratch = self.root / "task-scratch"
        self.request = self.root / "worker-request.json"
        self.request.write_text('{"p":"9223372021248595841","variables":["x"],"equations":[]}\n')

    def admitted(self):
        return {"plan": fake_plan(), "plan_path": str(self.plan),
                "plan_sha256": self.plan_sha, "owner": "test-owner", "epoch": 3,
                "authorization": {"owner": "test-owner", "epoch": 3},
                "selector_execution_state": "ready"}

    def test_frozen_schedule_and_machine_protections(self):
        source = execute.OLD / "execute.py"
        spec = importlib.util.spec_from_file_location("frozen_prime63_launcher", source)
        frozen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frozen)
        candidate, archived = execute.schedule(), frozen.schedule()
        self.assertEqual(len(candidate), 27)
        self.assertEqual(json.dumps(candidate, sort_keys=True), json.dumps(archived, sort_keys=True))
        self.assertEqual((execute.CALL_SECONDS, execute.RSS_CAP, execute.SCRATCH_CAP,
                          execute.MODEL_CAP, execute.PANEL_SECONDS, execute.START_FREE,
                          execute.CONTINUE_FREE),
                         (300, 8*1024**3, 8*1024**3, 64, 4*3600,
                          16*1024**3, 8*1024**3))
        print(json.dumps({"control": "frozen_schedule", "cells": len(candidate),
                          "identical_to_archived": True}, sort_keys=True))

    def _entry_refuses_without_side_effect(self, mode, admission_error):
        args = (["execute.py", "--run-approved", "--plan", str(self.plan),
                 "--owner", "test-owner", "--epoch", "3", "--output", str(self.out)]
                if mode == "parent" else
                ["execute.py", "--worker-request", str(self.request),
                 "--worker-output", str(self.worker_output), "--plan", str(self.plan),
                 "--owner", "test-owner", "--epoch", "3"])
        with patch.object(sys, "argv", args), patch.object(execute, "ROOT", self.root), \
             patch.object(execute, "SCRATCH", self.scratch), \
             patch.object(execute, "admit", side_effect=admission_error) as gate, \
             patch.object(execute, "worker") as worker, \
             patch.object(execute.subprocess, "Popen") as spawn:
            with self.assertRaisesRegex(execute.execution.ExecutionError, str(admission_error)):
                execute.main()
            self.assertEqual(gate.call_count, 1)
            worker.assert_not_called()
            spawn.assert_not_called()
        self.assertFalse(self.scratch.exists())
        self.assertFalse(self.out.exists())
        self.assertFalse(self.worker_output.exists())

    def test_both_entrypoints_fail_closed_for_repository_rejections(self):
        reasons = [
            "forged approval status strings", "wrong decision binding",
            "wrong plan hash", "wrong specification hash", "changed source hash",
            "review_required selector", "absent published claim", "expired claim",
            "wrong claim owner", "wrong claim epoch",
        ]
        for reason in reasons:
            for mode in ("parent", "worker"):
                with self.subTest(reason=reason, mode=mode):
                    self._entry_refuses_without_side_effect(mode,
                        execute.execution.ExecutionError(reason))
        print(json.dumps({"control": "entrypoint_fail_closed", "cases": len(reasons)*2,
                          "scratch_created": False, "output_created": False,
                          "worker_spawned": False}, sort_keys=True))

    def test_admit_load_plan_hash_errors_precede_authorize(self):
        for reason in ("wrong plan hash", "wrong specification hash", "changed source hash"):
            with self.subTest(reason=reason), \
                 patch.object(execute.execution, "load_plan",
                              side_effect=execute.execution.ExecutionError(reason)) as load, \
                 patch.object(execute.execution, "authorize") as auth, \
                 patch.object(execute.newest_experiments, "newest_runnable") as selector:
                with self.assertRaisesRegex(execute.execution.ExecutionError, reason):
                    execute.admit(self.plan, "test-owner", 3, root=self.root)
                load.assert_called_once()
                auth.assert_not_called()
                selector.assert_not_called()

    def test_admit_dispatch_claim_and_decision_errors_precede_selector(self):
        for reason in ("wrong decision binding", "absent published claim", "expired claim",
                       "wrong claim owner", "wrong claim epoch"):
            with self.subTest(reason=reason), \
                 patch.object(execute.execution, "load_plan", return_value=fake_plan()) as load, \
                 patch.object(execute.execution, "authorize",
                              side_effect=execute.execution.ExecutionError(reason)) as auth, \
                 patch.object(execute.newest_experiments, "newest_runnable") as selector:
                with self.assertRaisesRegex(execute.execution.ExecutionError, reason):
                    execute.admit(self.plan, "test-owner", 3, root=self.root)
                load.assert_called_once()
                auth.assert_called_once_with(self.root.resolve(), self.plan, fake_plan(),
                                             "test-owner", 3)
                selector.assert_not_called()

    def test_admit_rejects_review_required_selector_and_wrong_plan(self):
        for result in (
            {"id": "EXP-PRIME63-abcdef", "execution_state": "review_required",
             "trial_plan": self.relative},
            {"id": "EXP-PRIME63-abcdef", "execution_state": "ready",
             "trial_plan": "experiments/other/trial-plan.json",
             "coverage": {"plan_sha256": self.plan_sha}},
            {"id": "EXP-PRIME63-abcdef", "execution_state": "ready",
             "trial_plan": self.relative,
             "coverage": {"plan_sha256": "0" * 64}},
            {},  # the public selector omits review_required specifications
        ):
            with self.subTest(result=result), \
                 patch.object(execute.execution, "load_plan", return_value=fake_plan()), \
                 patch.object(execute.execution, "authorize", return_value={"owner": "test-owner"}), \
                 patch.object(execute.newest_experiments, "newest_runnable",
                              return_value=[result] if result else []):
                with self.assertRaisesRegex(execute.execution.ExecutionError, "selector is not ready"):
                    execute.admit(self.plan, "test-owner", 3, root=self.root)

    def test_admit_uses_exact_public_selector_core(self):
        row = {"id": "EXP-PRIME63-abcdef", "execution_state": "ready",
               "trial_plan": self.relative, "coverage": {"plan_sha256": self.plan_sha}}
        with patch.object(execute.execution, "load_plan", return_value=fake_plan()) as load, \
             patch.object(execute.execution, "authorize", return_value={"owner": "test-owner"}) as auth, \
             patch.object(execute.newest_experiments, "newest_runnable", return_value=[row]) as select:
            result = execute.admit(self.plan, "test-owner", 3, root=self.root)
            load.assert_called_once()
            auth.assert_called_once()
            select.assert_called_once_with(repo=self.root.resolve(),
                                           experiment_ids={"EXP-PRIME63-abcdef"})
            self.assertEqual((result["selector_execution_state"], result["plan_sha256"]),
                             ("ready", self.plan_sha))

    def test_caller_approval_packet_is_not_an_entrypoint(self):
        packet = self.root / "forged.json"
        packet.write_text(json.dumps({"status": "approved", "selector_execution_state": "ready",
                                      "task_id": "TASK-20261017-4d8c00"}))
        argv = ["execute.py", "--run-approved", "--approval-packet", str(packet),
                "--output", str(self.out)]
        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(io.StringIO()), \
             patch.object(execute.subprocess, "Popen") as spawn:
            with self.assertRaises(SystemExit) as stopped:
                execute.main()
            self.assertEqual(stopped.exception.code, 2)
            spawn.assert_not_called()
        self.assertFalse(self.out.exists())

    def test_real_cli_rejects_unfrozen_plan_before_side_effects(self):
        for mode in ("parent", "worker"):
            argv = ([sys.executable, str(HERE / "execute.py"), "--run-approved",
                     "--plan", str(self.plan), "--owner", "forged", "--epoch", "3",
                     "--output", str(self.out)] if mode == "parent" else
                    [sys.executable, str(HERE / "execute.py"), "--worker-request",
                     str(self.request), "--worker-output", str(self.worker_output),
                     "--plan", str(self.plan), "--owner", "forged", "--epoch", "3"])
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("trial plan must use the supported schema", result.stderr)
            self.assertFalse(self.out.exists())
            self.assertFalse(self.worker_output.exists())
            self.assertFalse(self.scratch.exists())
        print(json.dumps({"control": "real_cli_unfrozen_plan_refusal",
                          "entrypoints": 2, "output_created": False}, sort_keys=True))

    def test_mocked_positive_forwards_exact_plan_owner_epoch(self):
        # This is a command-forwarding control. It does not establish a real
        # approved EXP, selector or published claim.
        with patch.object(execute, "admit", return_value=self.admitted()) as gate, \
             patch.object(execute, "SCRATCH", self.scratch), \
             patch.object(execute, "START_FREE", 0), \
             patch.object(execute, "schedule", return_value=[
                 {"id": f"cell-{i}", "kind": "natural", "arm": "random", "m": 2,
                  "request": {"p": "101", "variables": ["x"], "equations": []}}
                 for i in range(27)]), \
             patch.object(execute, "supervise") as supervisor:
            def fake_supervisor(command, env, stdout, stderr, deadline):
                stdout.write_text("mock worker\n")
                stderr.write_text("")
                (stdout.parent / "response.json").write_text('{"status":"ok","root_count":0,"roots":[]}\n')
                return {"stop": "exited", "exit_code": 0, "command": command,
                        "started_utc": "mock", "ended_utc": "mock", "wall_seconds": 0,
                        "cpu_user_seconds": 0, "cpu_system_seconds": 0,
                        "peak_tree_rss_bytes_sampled": 0, "peak_scratch_bytes_sampled": 0,
                        "minimum_free_bytes_sampled": shutil.disk_usage(self.root).free,
                        "poll_seconds": execute.POLL_SECONDS,
                        "stdout_sha256": execute.sha(stdout), "stderr_sha256": execute.sha(stderr)}
            supervisor.side_effect = fake_supervisor
            result = execute.create_panel(self.plan, "test-owner", 3, self.out)
            gate.assert_called_once_with(self.plan, "test-owner", 3)
            self.assertEqual((result["attempted"], result["unattempted"]), (27, 0))
            self.assertEqual(supervisor.call_count, 27)
            for call in supervisor.call_args_list:
                command = call.args[0]
                self.assertEqual(command[-6:], ["--plan", str(self.plan),
                                                "--owner", "test-owner", "--epoch", "3"])
            print(json.dumps({"control": "mock_forwarding", "calls": supervisor.call_count,
                              "plan": str(self.plan), "owner": "test-owner", "epoch": 3}, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
