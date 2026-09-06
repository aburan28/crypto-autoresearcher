from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import resource
import sys
import tempfile
import unittest
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

from crypto_autoresearcher import runner as runner_module
from crypto_autoresearcher.records import (
    RecordValidationError,
    canonical_json_bytes,
    find_repo_root,
    read_json,
    validate_record,
    write_json,
)
from crypto_autoresearcher.runner import run_experiment


REPO_ROOT = find_repo_root(Path(__file__).parent)
BASE_COMMIT = "a" * 40
VERIFIER_COMMIT = "b" * 40


class RunnerTests(unittest.TestCase):
    def _test_effective_uid(self) -> int:
        return os.geteuid() or 1

    def setUp(self):
        # Existing low-level cap tests exercise the exceptional enforcement path.
        # Real review receipts and the ordinary default have separate regressions.
        self.enforcement = patch.object(runner_module, "enforce_research_budget", return_value=True)
        self.enforcement.start()
        self.addCleanup(self.enforcement.stop)

    def _specification(self) -> dict:
        return {
            "experiment": {
                "id": "EXP-TEST-001",
                "hypothesis_id": "H-TEST-001",
                "version": 1,
                "title": "Runner test",
                "status": "draft",
                "objective": "Exercise immutable artifact capture.",
                "inputs": {},
                "controls": ["known JSON command"],
                "independent_variables": ["none"],
                "metrics": {"primary": ["answer"], "secondary": []},
                "replication": {"seeds": [7], "independent_instances": 1},
                "budget": {
                    "wall_clock_seconds_per_run": 5,
                    "total_cpu_hours": 0.01,
                    "maximum_memory_gb": 1,
                    "maximum_runs": 1,
                },
                "stopping_rules": [],
                "invalidation_rules": [],
                "success_criterion": "JSON exits zero",
                "falsification_criterion": "JSON does not exit zero",
                "required_artifacts": ["manifest.json"],
                "assigned_to": "executor",
                "approved_by": None,
            }
        }

    def _write_specification(self, experiment_dir: Path, specification: dict) -> None:
        (experiment_dir / "specification.json").write_text(
            json.dumps(specification), encoding="utf-8"
        )

    def _valid_command(self) -> list[str]:
        return [
            sys.executable,
            "-c",
            "import json; print(json.dumps({'valid': True, 'summary': {'answer': 42}}))",
        ]

    def _write_script(self, experiment_dir: Path, name: str, body: str) -> Path:
        path = experiment_dir / name
        path.write_text(body, encoding="utf-8")
        return path

    def _source_command(self, source: Path, *arguments: str) -> list[str]:
        return [
            str(Path(sys.executable).resolve()),
            "-I",
            "-S",
            "-B",
            source.resolve().relative_to(REPO_ROOT).as_posix(),
            *arguments,
        ]

    def _protocol_hashes(
        self, experiment_dir: Path, *extra_paths: Path
    ) -> list[dict[str, str]]:
        contract_path = experiment_dir / "contract.md"
        if not contract_path.exists():
            contract_path.write_text("Synthetic runner test contract.\n", encoding="utf-8")
        paths = (
            Path(runner_module.__file__).resolve(),
            REPO_ROOT / "src" / "crypto_autoresearcher" / "__init__.py",
            REPO_ROOT / "src" / "crypto_autoresearcher" / "cli.py",
            REPO_ROOT / "src" / "crypto_autoresearcher" / "records.py",
            REPO_ROOT / "schemas" / "experiment.schema.json",
            REPO_ROOT / "schemas" / "run-manifest.schema.json",
            REPO_ROOT / "schemas" / "execution-approval.schema.json",
            REPO_ROOT / "schemas" / "runner-receipt.schema.json",
            contract_path,
            *extra_paths,
        )
        unique_paths = list(dict.fromkeys(path.resolve() for path in paths))
        return [
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in unique_paths
        ]

    def _planned_specification(
        self,
        experiment_dir: Path,
        runs: list[dict],
        *sources: Path,
    ) -> dict:
        specification = self._specification()
        specification["experiment"]["status"] = "approved"
        specification["experiment"]["approved_by"] = "test-coordinator"
        specification["experiment"]["budget"]["maximum_runs"] = len(runs)
        specification["experiment"]["execution_plan"] = {
            "allow_dirty": False,
            "protocol_hashes": self._protocol_hashes(experiment_dir, *sources),
            "runs": runs,
        }
        self._write_specification(experiment_dir, specification)
        return specification

    def _approval_lock(
        self,
        lock_dir: Path,
        experiment_dir: Path,
        specification: dict,
        *,
        base_commit: str = BASE_COMMIT,
        python_version: str | None = None,
        effective_uid: int | None = None,
        transitions: list[dict[str, str]] | None = None,
        name: str = "execution-approval.json",
    ) -> tuple[Path, str]:
        plan = specification["experiment"]["execution_plan"]
        if transitions is None:
            transitions = [
                {
                    "verifier_run_id": run["run_id"],
                    "predecessor_run_id": run["predecessor"]["run_id"],
                    "artifact": "raw-result.json",
                    "commit_policy": "base-plus-committed-predecessor-run-only",
                }
                for run in plan["runs"]
                if run["role"] == "verifier"
            ]
        python_path = Path(sys.executable).resolve()
        approval = {
            "execution_approval": {
                "format_version": 1,
                "experiment_id": specification["experiment"]["id"],
                "approved_base_commit": base_commit,
                "specification_sha256": hashlib.sha256(
                    (experiment_dir / "specification.json").read_bytes()
                ).hexdigest(),
                "execution_plan_sha256": hashlib.sha256(
                    canonical_json_bytes(plan)
                ).hexdigest(),
                "protocol_hashes": plan["protocol_hashes"],
                "python": {
                    "executable": str(python_path),
                    "version": python_version or platform.python_version(),
                    "sha256": hashlib.sha256(python_path.read_bytes()).hexdigest(),
                },
                "resource_policy": {
                    "descendant_policy": runner_module.LOCKED_DESCENDANT_POLICY,
                    "effective_uid": (
                        self._test_effective_uid()
                        if effective_uid is None
                        else effective_uid
                    ),
                },
                "allowed_verifier_transitions": transitions,
            }
        }
        path = lock_dir / name
        write_json(path, approval)
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def _run_planned(
        self,
        experiment_dir: Path,
        run_id: str,
        lock_path: Path,
        lock_sha256: str,
        *,
        command: list[str] | None = None,
        seed: int | None = None,
        curve_id: str | None = None,
        parameters: dict | None = None,
        timeout_seconds: float | None = None,
        allow_dirty: bool = False,
    ) -> Path:
        specification = read_json(experiment_dir / "specification.json")
        planned = next(
            run
            for run in specification["experiment"]["execution_plan"]["runs"]
            if run["run_id"] == run_id
        )
        policy_context = (
            patch.object(
                runner_module,
                "_locked_resource_policy",
                return_value={
                    "descendant_policy": runner_module.LOCKED_DESCENDANT_POLICY,
                    "effective_uid": self._test_effective_uid(),
                },
            )
            if os.geteuid() == 0
            else nullcontext()
        )
        with policy_context:
            return run_experiment(
                repo_root=REPO_ROOT,
                experiment_dir=experiment_dir,
                run_id=run_id,
                command=planned["argv"] if command is None else command,
                seed=planned["seed"] if seed is None else seed,
                curve_id=planned["curve_id"] if curve_id is None else curve_id,
                parameters=planned["parameters"] if parameters is None else parameters,
                timeout_seconds=timeout_seconds,
                allow_dirty=allow_dirty,
                approval_lock_path=lock_path,
                approval_lock_sha256=lock_sha256,
            )

    def _checks(self, **overrides: bool) -> dict[str, bool]:
        checks = {key: True for key in runner_module.POST_RUN_CHECK_KEYS}
        checks.update(overrides)
        return checks

    def _fake_child(
        self, *, cpu_seconds: float, peak_rss_bytes: int = 1024
    ):
        def execute(**kwargs):
            stdout = json.dumps({"valid": True, "summary": {"answer": 42}})
            kwargs["stdout_path"].write_text(stdout, encoding="utf-8")
            kwargs["stderr_path"].write_text("", encoding="utf-8")
            return runner_module._ChildResult(
                return_code=0,
                timed_out=False,
                memory_killed=False,
                infrastructure_error=None,
                stdout=stdout,
                stderr="",
                cpu_seconds=cpu_seconds,
                peak_rss_bytes=peak_rss_bytes,
            )

        return execute

    def test_advisory_real_child_has_no_implicit_cpu_or_wall_limit(self):
        from orchestration.research_budget import enforce_research_budget
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            spec = self._specification()
            spec["experiment"]["budget"].update(
                wall_clock_seconds_per_run=None, total_cpu_hours=None,
                maximum_runs=None)
            self._write_specification(experiment_dir, spec)
            with patch.object(runner_module, "enforce_research_budget",
                              side_effect=enforce_research_budget):
                result = run_experiment(
                    repo_root=REPO_ROOT, experiment_dir=experiment_dir,
                    run_id="RUN-TEST-092", command=self._valid_command(), seed=7,
                    curve_id=None, parameters={}, timeout_seconds=None,
                    allow_dirty=True)
            manifest = read_json(result / "manifest.json")["run"]
            self.assertEqual(manifest["status"], "completed_valid")
            policy = manifest["environment"]["research_budget_policy"]
            self.assertEqual(policy["enforcement"], "advisory")
            self.assertIsNone(policy["process_watchdog_seconds"])

    def test_advisory_estimates_do_not_block_repeated_development_runs(self):
        from orchestration.research_budget import enforce_research_budget
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            spec = self._specification()
            spec["experiment"]["budget"].update({
                "wall_clock_seconds_per_run": None, "total_cpu_hours": 0,
                "maximum_runs": 1})
            self._write_specification(experiment_dir, spec)
            def child(**kwargs):
                self.assertIsNone(kwargs["timeout_seconds"])
                self.assertTrue(math.isinf(kwargs["cpu_seconds"]))
                return self._fake_child(cpu_seconds=100)(**kwargs)
            with patch.object(runner_module, "enforce_research_budget",
                              side_effect=enforce_research_budget), patch.object(
                                  runner_module, "_run_child", side_effect=child):
                for run_id in ("RUN-TEST-090", "RUN-TEST-091"):
                    result = run_experiment(
                        repo_root=REPO_ROOT, experiment_dir=experiment_dir,
                        run_id=run_id, command=self._valid_command(), seed=7,
                        curve_id=None, parameters={}, timeout_seconds=None,
                        allow_dirty=True)
                    manifest = read_json(result / "manifest.json")["run"]
                    self.assertEqual(manifest["status"], "completed_valid")
                    self.assertEqual(manifest["resources"]["cpu_seconds"], 100)

    def test_run_is_captured_and_duplicate_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            self._write_specification(experiment_dir, self._specification())
            command = self._valid_command()
            run_dir = run_experiment(
                repo_root=REPO_ROOT,
                experiment_dir=experiment_dir,
                run_id="RUN-TEST-001",
                command=command,
                seed=7,
                curve_id=None,
                parameters={},
                timeout_seconds=5,
                allow_dirty=True,
            )
            manifest = read_json(run_dir / "manifest.json")["run"]
            self.assertEqual(manifest["status"], "completed_valid")
            self.assertEqual(manifest["result"]["metrics"], {"answer": 42})
            self.assertIn("raw-result.json", manifest["artifacts"])
            self.assertNotIn("protocol", manifest)
            self.assertFalse(any(run_dir.rglob("._*")))
            with self.assertRaises(RecordValidationError):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-001",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )

    def test_child_memory_is_not_charged_the_parents_pre_exec_rss(self) -> None:
        # Regression for issue #702. `_wait_for_child` launches the run
        # command with `preexec_fn` on POSIX, which forces CPython to
        # `fork()` rather than `posix_spawn()`. A forked child's `ru_maxrss`
        # (as reported to the reaping `os.wait4` call) includes the RSS the
        # child inherited from the parent at fork time, before `exec()`
        # replaced its image. Folding that value into the run's observed
        # peak RSS meant a run launched from a large parent process (a
        # harness or a full pytest session) could be classified
        # `resource_exhaustion` regardless of what the run itself did.
        #
        # This inflates *this test process's* RSS well past the run's 1 GB
        # `maximum_memory_gb` budget before launching a trivial, well-behaved
        # command, and asserts the run still completes normally.
        ballast = bytearray(1300 * 1024 * 1024)  # ~1.3 GiB
        try:
            self.assertGreater(
                runner_module._max_rss_bytes(resource.getrusage(resource.RUSAGE_SELF)),
                1024 * 1024 * 1024,
            )
            with tempfile.TemporaryDirectory() as temporary:
                experiment_dir = Path(temporary) / "EXP-TEST-001"
                experiment_dir.mkdir()
                self._write_specification(experiment_dir, self._specification())
                run_dir = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-002",
                    command=self._valid_command(),
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )
                manifest = read_json(run_dir / "manifest.json")["run"]
                self.assertEqual(manifest["status"], "completed_valid")
        finally:
            del ballast

    def test_exit_zero_without_exact_valid_true_is_invalid(self) -> None:
        cases = [
            "print('not json')",
            "import json; print(json.dumps({'valid': 1, 'summary': {}}))",
            "import json; print(json.dumps({'summary': {}}))",
            "print('{\"valid\": true, \"value\": NaN}')",
        ]
        for index, program in enumerate(cases):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as temporary:
                experiment_dir = Path(temporary) / "EXP-TEST-001"
                experiment_dir.mkdir()
                self._write_specification(experiment_dir, self._specification())
                run_dir = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id=f"RUN-TEST-{index + 10:03d}",
                    command=[sys.executable, "-c", program],
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )
                manifest = read_json(run_dir / "manifest.json")["run"]
                self.assertEqual(manifest["status"], "completed_invalid")

    def test_zero_budgets_reject_before_launch(self) -> None:
        cases = (
            ("wall_clock_seconds_per_run", 0),
            ("total_cpu_hours", 0),
            ("maximum_memory_gb", 0),
            ("maximum_runs", 0),
        )
        for field, value in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                experiment_dir = Path(temporary) / "EXP-TEST-001"
                experiment_dir.mkdir()
                sentinel = Path(temporary) / "launched"
                specification = self._specification()
                specification["experiment"]["budget"][field] = value
                self._write_specification(experiment_dir, specification)
                command = [
                    sys.executable,
                    "-c",
                    "from pathlib import Path; import json, sys; "
                    "Path(sys.argv[1]).write_text('launched'); "
                    "print(json.dumps({'valid': True}))",
                    str(sentinel),
                ]
                with self.assertRaises(RecordValidationError):
                    run_experiment(
                        repo_root=REPO_ROOT,
                        experiment_dir=experiment_dir,
                        run_id="RUN-TEST-020",
                        command=command,
                        seed=7,
                        curve_id=None,
                        parameters={},
                        timeout_seconds=5,
                        allow_dirty=True,
                    )
                self.assertFalse(sentinel.exists())

    def test_caller_timeout_is_bounded_and_default_is_capped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            specification = self._specification()
            specification["experiment"]["budget"][
                "wall_clock_seconds_per_run"
            ] = 0.05
            self._write_specification(experiment_dir, specification)
            sentinel = Path(temporary) / "launched"
            command = [
                sys.executable,
                "-c",
                "import json, sys, time; from pathlib import Path; "
                "Path(sys.argv[1]).write_text('launched'); time.sleep(1); "
                "print(json.dumps({'valid': True}))",
                str(sentinel),
            ]
            with self.assertRaisesRegex(RecordValidationError, "caller timeout_seconds"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-021",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=1,
                    allow_dirty=True,
                )
            self.assertFalse(sentinel.exists())
            run_dir = run_experiment(
                repo_root=REPO_ROOT,
                experiment_dir=experiment_dir,
                run_id="RUN-TEST-021",
                command=command,
                seed=7,
                curve_id=None,
                parameters={},
                timeout_seconds=None,
                allow_dirty=True,
            )
            manifest = read_json(run_dir / "manifest.json")["run"]
            self.assertEqual(manifest["status"], "resource_exhaustion")
            self.assertIn("wall-clock limit", manifest["result"]["invalid_reason"])

    def test_maximum_runs_rejects_a_distinct_second_run_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            self._write_specification(experiment_dir, self._specification())
            run_experiment(
                repo_root=REPO_ROOT,
                experiment_dir=experiment_dir,
                run_id="RUN-TEST-030",
                command=self._valid_command(),
                seed=7,
                curve_id=None,
                parameters={},
                timeout_seconds=5,
                allow_dirty=True,
            )
            sentinel = Path(temporary) / "second-launched"
            second_command = [
                sys.executable,
                "-c",
                "from pathlib import Path; import json, sys; "
                "Path(sys.argv[1]).write_text('launched'); "
                "print(json.dumps({'valid': True}))",
                str(sentinel),
            ]
            with self.assertRaisesRegex(RecordValidationError, "maximum_runs exhausted"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-031",
                    command=second_command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )
            self.assertFalse(sentinel.exists())

    def test_cumulative_cpu_budget_includes_current_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            specification = self._specification()
            specification["experiment"]["budget"].update(
                {"maximum_runs": 2, "total_cpu_hours": 0.00001}
            )
            self._write_specification(experiment_dir, specification)
            fake_children = iter(
                [
                    self._fake_child(cpu_seconds=0.02),
                    self._fake_child(cpu_seconds=0.02),
                ]
            )

            def run_fake_child(**kwargs):
                return next(fake_children)(**kwargs)

            with patch.object(runner_module, "_run_child", side_effect=run_fake_child):
                first = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-040",
                    command=self._valid_command(),
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )
                second = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-041",
                    command=self._valid_command(),
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )
            self.assertEqual(
                read_json(first / "manifest.json")["run"]["status"],
                "completed_valid",
            )
            second_manifest = read_json(second / "manifest.json")["run"]
            self.assertEqual(second_manifest["status"], "resource_exhaustion")
            self.assertIn(
                "cumulative CPU budget exceeded",
                second_manifest["result"]["invalid_reason"],
            )

    def test_child_memory_budget_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            specification = self._specification()
            specification["experiment"]["budget"]["maximum_memory_gb"] = 0.0625
            self._write_specification(experiment_dir, specification)
            command = [
                sys.executable,
                "-c",
                "import json, time; payload = bytearray(128 * 1024 * 1024); "
                "time.sleep(0.2); print(json.dumps({'valid': True, 'bytes': len(payload)}))",
            ]
            run_dir = run_experiment(
                repo_root=REPO_ROOT,
                experiment_dir=experiment_dir,
                run_id="RUN-TEST-050",
                command=command,
                seed=7,
                curve_id=None,
                parameters={},
                timeout_seconds=5,
                allow_dirty=True,
            )
            manifest = read_json(run_dir / "manifest.json")["run"]
            self.assertEqual(manifest["status"], "resource_exhaustion")
            self.assertIn("memory budget", manifest["result"]["invalid_reason"])

    def test_execution_plan_rejects_argv_dirty_and_open_schema(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            command = self._source_command(source)
            run = {
                "run_id": "RUN-TEST-060",
                "role": "generator",
                "argv": command,
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            validate_record(experiment_dir / "specification.json", REPO_ROOT)
            with self.assertRaisesRegex(RecordValidationError, "argv"):
                self._run_planned(
                    experiment_dir,
                    run["run_id"],
                    lock_path,
                    lock_sha,
                    command=[*command, "unexpected"],
                )
            with self.assertRaisesRegex(RecordValidationError, "forbids allow_dirty"):
                self._run_planned(
                    experiment_dir,
                    run["run_id"],
                    lock_path,
                    lock_sha,
                    allow_dirty=True,
                )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": BASE_COMMIT, "dirty": True},
            ), self.assertRaisesRegex(RecordValidationError, "working tree is dirty"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            specification["experiment"]["execution_plan"]["allow_dirty"] = True
            self._write_specification(experiment_dir, specification)
            with self.assertRaisesRegex(RecordValidationError, "expected constant False"):
                validate_record(experiment_dir / "specification.json", REPO_ROOT)
            specification["experiment"]["execution_plan"]["allow_dirty"] = False
            specification["experiment"]["execution_plan"]["unexpected"] = True
            self._write_specification(experiment_dir, specification)
            with self.assertRaisesRegex(RecordValidationError, "unexpected key"):
                validate_record(experiment_dir / "specification.json", REPO_ROOT)

    def test_locked_execution_plan_requires_external_lock(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-061",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            self._planned_specification(experiment_dir, [run], source)
            with self.assertRaisesRegex(RecordValidationError, "require --approval-lock"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id=run["run_id"],
                    command=run["argv"],
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=False,
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_approved_experiment_cannot_remove_execution_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            specification = self._specification()
            specification["experiment"]["status"] = "approved"
            specification["experiment"]["approved_by"] = "test-coordinator"
            self._write_specification(experiment_dir, specification)
            sentinel = Path(temporary) / "plan-bypass-launched"
            command = [
                sys.executable,
                "-c",
                f"from pathlib import Path; Path({str(sentinel)!r}).write_text('bad')",
            ]
            for allow_dirty in (False, True):
                with self.subTest(allow_dirty=allow_dirty), self.assertRaisesRegex(
                    RecordValidationError, "lacks an approver or locked execution_plan"
                ):
                    run_experiment(
                        repo_root=REPO_ROOT,
                        experiment_dir=experiment_dir,
                        run_id="RUN-TEST-062",
                        command=command,
                        seed=7,
                        curve_id=None,
                        parameters={},
                        timeout_seconds=5,
                        allow_dirty=allow_dirty,
                    )
            self.assertFalse(sentinel.exists())
            self.assertFalse((experiment_dir / "runs").exists())

    def test_locked_graph_and_predecessor_sha_receipt_linkage(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            generator_source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True, 'payload': 17}))\n",
            )
            verifier_source = self._write_script(
                experiment_dir,
                "verifier.py",
                "import hashlib, json, sys\n"
                "raw = open(sys.argv[1], 'rb').read()\n"
                "print(json.dumps({'valid': True, 'input': "
                "{'sha256': hashlib.sha256(raw).hexdigest()}}))\n",
            )
            mismatch_source = self._write_script(
                experiment_dir,
                "mismatch.py",
                "import json\nprint(json.dumps({'valid': True, "
                "'input': {'sha256': '0' * 64}}))\n",
            )
            raw_path = (
                experiment_dir / "runs" / "RUN-TEST-070" / "raw-result.json"
            ).relative_to(REPO_ROOT).as_posix()
            runs = [
                {
                    "run_id": "RUN-TEST-070",
                    "role": "generator",
                    "argv": self._source_command(generator_source),
                    "seed": 7,
                    "curve_id": "toy-curve",
                    "parameters": {"phase": "generate"},
                    "timeout_seconds": 5,
                    "predecessor": None,
                },
                {
                    "run_id": "RUN-TEST-071",
                    "role": "verifier",
                    "argv": self._source_command(verifier_source, raw_path),
                    "seed": 7,
                    "curve_id": "toy-curve",
                    "parameters": {"phase": "verify"},
                    "timeout_seconds": 5,
                    "predecessor": {
                        "run_id": "RUN-TEST-070",
                        "artifact": "raw-result.json",
                    },
                },
                {
                    "run_id": "RUN-TEST-072",
                    "role": "verifier",
                    "argv": self._source_command(mismatch_source),
                    "seed": 7,
                    "curve_id": "toy-curve",
                    "parameters": {"phase": "mismatch"},
                    "timeout_seconds": 5,
                    "predecessor": {
                        "run_id": "RUN-TEST-070",
                        "artifact": "raw-result.json",
                    },
                },
            ]
            specification = self._planned_specification(
                experiment_dir,
                runs,
                generator_source,
                verifier_source,
                mismatch_source,
            )
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": BASE_COMMIT, "dirty": False},
            ), patch.object(
                runner_module, "_post_run_checks", return_value=self._checks()
            ):
                generator = self._run_planned(
                    experiment_dir, "RUN-TEST-070", lock_path, lock_sha
                )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": VERIFIER_COMMIT, "dirty": False},
            ), patch.object(
                runner_module, "_post_run_checks", return_value=self._checks()
            ), patch.object(
                runner_module, "_verify_committed_predecessor_transition"
            ):
                verifier = self._run_planned(
                    experiment_dir, "RUN-TEST-071", lock_path, lock_sha
                )
                mismatch = self._run_planned(
                    experiment_dir, "RUN-TEST-072", lock_path, lock_sha
                )
            generator_manifest = read_json(generator / "manifest.json")["run"]
            verifier_manifest = read_json(verifier / "manifest.json")["run"]
            mismatch_manifest = read_json(mismatch / "manifest.json")["run"]
            self.assertEqual(generator_manifest["status"], "completed_valid")
            self.assertEqual(verifier_manifest["status"], "completed_valid")
            self.assertEqual(mismatch_manifest["status"], "completed_invalid")
            self.assertIn(
                "input.sha256 does not match predecessor",
                mismatch_manifest["result"]["invalid_reason"],
            )
            self.assertEqual(
                verifier_manifest["receipt"]["predecessor"]["run_id"],
                "RUN-TEST-070",
            )
            self.assertEqual(
                verifier_manifest["protocol"]["execution_plan_sha256"],
                hashlib.sha256(
                    canonical_json_bytes(
                        specification["experiment"]["execution_plan"]
                    )
                ).hexdigest(),
            )
            validate_record(generator / "runner-receipt.json", REPO_ROOT)
            validate_record(verifier / "runner-receipt.json", REPO_ROOT)

    def test_execution_plan_graph_requires_generator_predecessor_first(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "run.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            command = self._source_command(source)
            runs = [
                {
                    "run_id": "RUN-TEST-081",
                    "role": "verifier",
                    "argv": command,
                    "seed": 7,
                    "curve_id": None,
                    "parameters": {},
                    "timeout_seconds": 5,
                    "predecessor": {
                        "run_id": "RUN-TEST-080",
                        "artifact": "raw-result.json",
                    },
                },
                {
                    "run_id": "RUN-TEST-080",
                    "role": "generator",
                    "argv": command,
                    "seed": 7,
                    "curve_id": None,
                    "parameters": {},
                    "timeout_seconds": 5,
                    "predecessor": None,
                },
            ]
            self._planned_specification(experiment_dir, runs, source)
            with self.assertRaisesRegex(RecordValidationError, "must appear earlier"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-080",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=False,
                )

    def test_external_lock_rejects_clean_specification_plan_replacement(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            original = self._write_script(
                experiment_dir,
                "original.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-090",
                "role": "generator",
                "argv": self._source_command(original),
                "seed": 7,
                "curve_id": None,
                "parameters": {"version": 1},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], original)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            replacement = self._write_script(
                experiment_dir,
                "replacement.py",
                "import json\nprint(json.dumps({'valid': True, 'replacement': True}))\n",
            )
            replacement_run = {
                **run,
                "argv": self._source_command(replacement),
                "seed": 99,
                "parameters": {"version": 2},
            }
            self._planned_specification(
                experiment_dir, [replacement_run], replacement
            )
            with self.assertRaisesRegex(
                RecordValidationError, "specification SHA-256 does not match"
            ):
                self._run_planned(
                    experiment_dir,
                    replacement_run["run_id"],
                    lock_path,
                    lock_sha,
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_locked_plan_forbids_inline_python(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            run = {
                "run_id": "RUN-TEST-091",
                "role": "generator",
                "argv": self._valid_command(),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run])
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with self.assertRaisesRegex(RecordValidationError, "forbids inline -c"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_locked_plan_requires_python_isolation_flags(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-095",
                "role": "generator",
                "argv": [
                    str(Path(sys.executable).resolve()),
                    source.relative_to(REPO_ROOT).as_posix(),
                ],
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with self.assertRaisesRegex(RecordValidationError, "isolation flags"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_locked_plan_requires_absolute_python(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-096",
                "role": "generator",
                "argv": [
                    Path(sys.executable).name,
                    "-I",
                    "-S",
                    "-B",
                    source.relative_to(REPO_ROOT).as_posix(),
                ],
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with self.assertRaisesRegex(RecordValidationError, "absolute approved"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_external_lock_and_protocol_reject_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-092",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            source.write_text(
                "import json\nprint(json.dumps({'valid': False}))\n",
                encoding="utf-8",
            )
            with patch.object(runner_module, "_git_state") as git_state, self.assertRaisesRegex(
                RecordValidationError, "protocol SHA-256 mismatch"
            ):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            git_state.assert_not_called()
            self.assertFalse((experiment_dir / "runs").exists())

    def test_protocol_rejects_parent_traversal_before_reservation(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-093",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            specification["experiment"]["execution_plan"]["protocol_hashes"].insert(
                0, {"path": "../escape.py", "sha256": "0" * 64}
            )
            self._write_specification(experiment_dir, specification)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with self.assertRaisesRegex(RecordValidationError, "parent traversal"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_protocol_rejects_hard_link_alias_identity(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-094",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            contract = experiment_dir / "contract.md"
            alias = experiment_dir / "contract-hard-link.md"
            stat_context = nullcontext()
            try:
                os.link(contract, alias)
            except OSError:
                alias.write_bytes(contract.read_bytes())
                original_stat = Path.stat
                alias_path = alias.resolve()
                contract_stat = contract.stat()

                def hard_link_stat(path: Path, *args, **kwargs):
                    result = original_stat(path, *args, **kwargs)
                    if path == alias_path:
                        values = list(result)
                        values[1] = contract_stat.st_ino
                        values[2] = contract_stat.st_dev
                        return os.stat_result(values)
                    return result

                stat_context = patch.object(Path, "stat", new=hard_link_stat)
            specification["experiment"]["execution_plan"]["protocol_hashes"].append(
                {
                    "path": alias.relative_to(REPO_ROOT).as_posix(),
                    "sha256": hashlib.sha256(alias.read_bytes()).hexdigest(),
                }
            )
            self._write_specification(experiment_dir, specification)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with stat_context, self.assertRaisesRegex(
                RecordValidationError, "duplicate protocol"
            ):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_strict_approval_lock_rejects_duplicate_and_nonfinite_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-095",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            for mode in ("duplicate", "nonfinite"):
                with self.subTest(mode=mode):
                    lock_path, _lock_sha = self._approval_lock(
                        Path(locks),
                        experiment_dir,
                        specification,
                        name=f"{mode}.json",
                    )
                    content = lock_path.read_text(encoding="utf-8")
                    if mode == "duplicate":
                        needle = '"experiment_id": "EXP-TEST-001"'
                        content = content.replace(
                            needle, f"{needle},\n    {needle}", 1
                        )
                    else:
                        content = content.replace('"format_version": 1', '"format_version": NaN')
                    lock_path.write_text(content, encoding="utf-8")
                    lock_sha = hashlib.sha256(lock_path.read_bytes()).hexdigest()
                    expected = "duplicate JSON" if mode == "duplicate" else "non-finite"
                    with self.assertRaisesRegex(RecordValidationError, expected):
                        self._run_planned(
                            experiment_dir,
                            run["run_id"],
                            lock_path,
                            lock_sha,
                        )

    def test_approval_lock_rejects_runtime_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-096",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks),
                experiment_dir,
                specification,
                python_version="0.0.invalid",
            )
            with self.assertRaisesRegex(RecordValidationError, "Python version"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_approval_lock_rejects_resource_policy_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-097",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks),
                experiment_dir,
                specification,
                effective_uid=self._test_effective_uid() + 1,
            )
            with self.assertRaisesRegex(RecordValidationError, "resource policy"):
                self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs").exists())

    def test_forged_predecessor_command_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            generator_source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True, 'payload': 3}))\n",
            )
            verifier_source = self._write_script(
                experiment_dir,
                "verifier.py",
                "import hashlib, json, sys\n"
                "raw = open(sys.argv[1], 'rb').read()\n"
                "print(json.dumps({'valid': True, 'input': "
                "{'sha256': hashlib.sha256(raw).hexdigest()}}))\n",
            )
            raw_path = (
                experiment_dir / "runs" / "RUN-TEST-100" / "raw-result.json"
            ).relative_to(REPO_ROOT).as_posix()
            runs = [
                {
                    "run_id": "RUN-TEST-100",
                    "role": "generator",
                    "argv": self._source_command(generator_source),
                    "seed": 7,
                    "curve_id": "toy",
                    "parameters": {"phase": "generate"},
                    "timeout_seconds": 5,
                    "predecessor": None,
                },
                {
                    "run_id": "RUN-TEST-101",
                    "role": "verifier",
                    "argv": self._source_command(verifier_source, raw_path),
                    "seed": 7,
                    "curve_id": "toy",
                    "parameters": {"phase": "verify"},
                    "timeout_seconds": 5,
                    "predecessor": {
                        "run_id": "RUN-TEST-100",
                        "artifact": "raw-result.json",
                    },
                },
            ]
            specification = self._planned_specification(
                experiment_dir, runs, generator_source, verifier_source
            )
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": BASE_COMMIT, "dirty": False},
            ), patch.object(
                runner_module, "_post_run_checks", return_value=self._checks()
            ):
                generator = self._run_planned(
                    experiment_dir, "RUN-TEST-100", lock_path, lock_sha
                )
            forged = read_json(generator / "manifest.json")
            forged["run"]["code"]["command"] = "forged generator command"
            write_json(generator / "manifest.json", forged)
            runner_module._remove_appledouble(generator)
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": VERIFIER_COMMIT, "dirty": False},
            ), self.assertRaisesRegex(RecordValidationError, "command does not match"):
                self._run_planned(
                    experiment_dir, "RUN-TEST-101", lock_path, lock_sha
                )
            self.assertFalse((experiment_dir / "runs" / "RUN-TEST-101").exists())

    def test_approval_commit_and_allowed_transition_rules(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            generator_source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            verifier_source = self._write_script(
                experiment_dir,
                "verifier.py",
                "import hashlib, json, sys\n"
                "raw = open(sys.argv[1], 'rb').read()\n"
                "print(json.dumps({'valid': True, 'input': "
                "{'sha256': hashlib.sha256(raw).hexdigest()}}))\n",
            )
            raw_path = (
                experiment_dir / "runs" / "RUN-TEST-110" / "raw-result.json"
            ).relative_to(REPO_ROOT).as_posix()
            runs = [
                {
                    "run_id": "RUN-TEST-110",
                    "role": "generator",
                    "argv": self._source_command(generator_source),
                    "seed": 7,
                    "curve_id": None,
                    "parameters": {},
                    "timeout_seconds": 5,
                    "predecessor": None,
                },
                {
                    "run_id": "RUN-TEST-111",
                    "role": "verifier",
                    "argv": self._source_command(verifier_source, raw_path),
                    "seed": 7,
                    "curve_id": None,
                    "parameters": {},
                    "timeout_seconds": 5,
                    "predecessor": {
                        "run_id": "RUN-TEST-110",
                        "artifact": "raw-result.json",
                    },
                },
            ]
            specification = self._planned_specification(
                experiment_dir, runs, generator_source, verifier_source
            )
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": VERIFIER_COMMIT, "dirty": False},
            ), self.assertRaisesRegex(RecordValidationError, "generator launch commit"):
                self._run_planned(
                    experiment_dir, "RUN-TEST-110", lock_path, lock_sha
                )
            bad_lock, bad_sha = self._approval_lock(
                Path(locks),
                experiment_dir,
                specification,
                transitions=[],
                name="bad-transitions.json",
            )
            with self.assertRaisesRegex(RecordValidationError, "transitions do not exactly"):
                self._run_planned(
                    experiment_dir, "RUN-TEST-110", bad_lock, bad_sha
                )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": BASE_COMMIT, "dirty": False},
            ), patch.object(
                runner_module, "_post_run_checks", return_value=self._checks()
            ):
                self._run_planned(
                    experiment_dir, "RUN-TEST-110", lock_path, lock_sha
                )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": VERIFIER_COMMIT, "dirty": False},
            ), patch.object(
                runner_module,
                "_verify_committed_predecessor_transition",
                side_effect=RecordValidationError("forbidden approval commit transition"),
            ), self.assertRaisesRegex(RecordValidationError, "forbidden approval commit"):
                self._run_planned(
                    experiment_dir, "RUN-TEST-111", lock_path, lock_sha
                )

    def test_post_launch_protocol_mutation_invalidates_locked_run(self) -> None:
        actual_head = runner_module._git(REPO_ROOT, "rev-parse", "HEAD")
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            contract = experiment_dir / "contract.md"
            contract.write_text("Original contract.\n", encoding="utf-8")
            source = self._write_script(
                experiment_dir,
                "mutator.py",
                "import json, sys\n"
                "from pathlib import Path\n"
                "Path(sys.argv[1]).write_text('mutated after launch\\n')\n"
                "print(json.dumps({'valid': True}))\n",
            )
            contract_argument = contract.relative_to(REPO_ROOT).as_posix()
            run = {
                "run_id": "RUN-TEST-120",
                "role": "generator",
                "argv": self._source_command(source, contract_argument),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks),
                experiment_dir,
                specification,
                base_commit=actual_head,
            )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": actual_head, "dirty": False},
            ), patch.object(runner_module, "_tree_clean_except", return_value=True):
                run_dir = self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            manifest = read_json(run_dir / "manifest.json")["run"]
            self.assertEqual(manifest["status"], "completed_invalid")
            self.assertFalse(
                manifest["protocol"]["post_run_checks"][
                    "protocol_hashes_unchanged"
                ]
            )

    def test_post_launch_tree_mutation_invalidates_locked_run(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json\nprint(json.dumps({'valid': True}))\n",
            )
            run = {
                "run_id": "RUN-TEST-121",
                "role": "generator",
                "argv": self._source_command(source),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            checks = self._checks(tree_unchanged=False)
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": BASE_COMMIT, "dirty": False},
            ), patch.object(
                runner_module, "_post_run_checks", return_value=checks
            ):
                run_dir = self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            manifest = read_json(run_dir / "manifest.json")["run"]
            self.assertEqual(manifest["status"], "completed_invalid")
            self.assertIn("tree_unchanged", manifest["result"]["invalid_reason"])

    def test_detached_descendants_are_charged_for_wall_cpu_and_memory(self) -> None:
        cases = (
            (
                "wall",
                {"wall_clock_seconds_per_run": 0.12},
                "import time; time.sleep(1)",
                "wall-clock limit",
            ),
            (
                "cpu",
                {"wall_clock_seconds_per_run": 2, "total_cpu_hours": 0.00005},
                "import time\nend = time.process_time() + 1\n"
                "while time.process_time() < end:\n    pass",
                "CPU budget",
            ),
            (
                "memory",
                {"wall_clock_seconds_per_run": 2, "maximum_memory_gb": 0.04},
                "import time\npayload = bytearray(96 * 1024 * 1024)\ntime.sleep(1)",
                "memory budget",
            ),
        )
        for index, (name, budget, descendant, reason) in enumerate(cases):
            with self.subTest(resource=name), tempfile.TemporaryDirectory() as temporary:
                experiment_dir = Path(temporary) / "EXP-TEST-001"
                experiment_dir.mkdir()
                specification = self._specification()
                specification["experiment"]["budget"].update(budget)
                self._write_specification(experiment_dir, specification)
                parent = (
                    "import json, subprocess, sys, time; "
                    f"subprocess.Popen([sys.executable, '-c', {descendant!r}], "
                    "start_new_session=True); "
                    "time.sleep(0.30); print(json.dumps({'valid': True}))"
                )
                run_dir = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id=f"RUN-TEST-{130 + index:03d}",
                    command=[sys.executable, "-c", parent],
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=None,
                    allow_dirty=True,
                )
                manifest = read_json(run_dir / "manifest.json")["run"]
                self.assertEqual(manifest["status"], "resource_exhaustion")
                self.assertIn(reason, manifest["result"]["invalid_reason"])

    @unittest.skipIf(
        os.name != "posix"
        or not hasattr(resource, "RLIMIT_NPROC")
        or os.geteuid() == 0,
        "locked descendant suppression requires non-root POSIX RLIMIT_NPROC",
    )
    def test_locked_run_forbids_instant_detached_descendant(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary, tempfile.TemporaryDirectory() as locks:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            marker = Path(temporary) / "escaped-descendant"
            source = self._write_script(
                experiment_dir,
                "generator.py",
                "import json, subprocess, sys\n"
                "try:\n"
                "    subprocess.Popen([sys.executable, '-c', "
                "'from pathlib import Path; import sys, time; time.sleep(0.1); "
                "Path(sys.argv[1]).write_text(\\\"escaped\\\")', sys.argv[1]], "
                "start_new_session=True)\n"
                "except OSError as exc:\n"
                "    print(json.dumps({'valid': True, 'summary': "
                "{'spawn_blocked': True, 'errno': exc.errno}}))\n"
                "else:\n"
                "    print(json.dumps({'valid': False, 'summary': "
                "{'spawn_blocked': False}}))\n",
            )
            run = {
                "run_id": "RUN-TEST-140",
                "role": "generator",
                "argv": self._source_command(source, str(marker)),
                "seed": 7,
                "curve_id": None,
                "parameters": {},
                "timeout_seconds": 5,
                "predecessor": None,
            }
            specification = self._planned_specification(experiment_dir, [run], source)
            lock_path, lock_sha = self._approval_lock(
                Path(locks), experiment_dir, specification
            )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": BASE_COMMIT, "dirty": False},
            ), patch.object(
                runner_module, "_post_run_checks", return_value=self._checks()
            ):
                run_dir = self._run_planned(
                    experiment_dir, run["run_id"], lock_path, lock_sha
                )
            manifest = read_json(run_dir / "manifest.json")["run"]
            raw = read_json(run_dir / "raw-result.json")
            self.assertEqual(manifest["status"], "completed_valid")
            self.assertTrue(raw["summary"]["spawn_blocked"])
            self.assertEqual(
                manifest["protocol"]["descendant_policy"],
                runner_module.LOCKED_DESCENDANT_POLICY,
            )
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
