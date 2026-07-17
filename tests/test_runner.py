from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from crypto_autoresearcher import runner as runner_module
from crypto_autoresearcher.records import (
    RecordValidationError,
    find_repo_root,
    validate_record,
)
from crypto_autoresearcher.runner import run_experiment


REPO_ROOT = find_repo_root(Path(__file__).parent)


class RunnerTests(unittest.TestCase):
    def _specification(self) -> dict:
        return {
            "experiment": {
                "id": "EXP-TEST-001",
                "hypothesis_id": "H-TEST-001",
                "version": 1,
                "title": "Runner test",
                "status": "approved",
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
                "approved_by": "test-coordinator",
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

    def _protocol_hashes(
        self, experiment_dir: Path, *extra_paths: Path
    ) -> list[dict[str, str]]:
        contract_path = experiment_dir / "contract.md"
        if not contract_path.exists():
            contract_path.write_text("Synthetic runner test contract.\n", encoding="utf-8")
        paths = (
            Path(runner_module.__file__).resolve(),
            REPO_ROOT / "schemas" / "experiment.schema.json",
            contract_path,
            *extra_paths,
        )
        return [
            {
                "path": path.resolve().relative_to(REPO_ROOT).as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in paths
        ]

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
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["run"]
            self.assertEqual(manifest["status"], "completed_valid")
            self.assertEqual(manifest["result"]["metrics"], {"answer": 42})
            self.assertIn("raw-result.json", manifest["artifacts"])
            self.assertFalse(any(run_dir.rglob("._*")))
            self.assertFalse(any(name.startswith("._") for name in manifest["artifacts"]))
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

    def test_exit_zero_without_exact_valid_true_is_invalid(self) -> None:
        cases = [
            "print('not json')",
            "import json; print(json.dumps({'valid': 1, 'summary': {}}))",
            "import json; print(json.dumps({'summary': {}}))",
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
                manifest = json.loads(
                    (run_dir / "manifest.json").read_text(encoding="utf-8")
                )["run"]
                self.assertEqual(manifest["status"], "completed_invalid")
                self.assertFalse(manifest["result"]["valid"])

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
            specification["experiment"]["budget"]["wall_clock_seconds_per_run"] = 0.05
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
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))[
                "run"
            ]
            self.assertTrue(sentinel.exists())
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

            with patch.object(
                runner_module, "_run_child", side_effect=run_fake_child
            ):
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

            first_manifest = json.loads(
                (first / "manifest.json").read_text(encoding="utf-8")
            )["run"]
            second_manifest = json.loads(
                (second / "manifest.json").read_text(encoding="utf-8")
            )["run"]
            self.assertEqual(first_manifest["status"], "completed_valid")
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
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))[
                "run"
            ]
            self.assertEqual(manifest["status"], "resource_exhaustion")
            self.assertIn("memory budget", manifest["result"]["invalid_reason"])

    def test_execution_plan_rejects_argv_and_dirty_policy(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            command = self._valid_command()
            specification = self._specification()
            specification["experiment"]["execution_plan"] = {
                "allow_dirty": False,
                "protocol_hashes": self._protocol_hashes(experiment_dir),
                "runs": [
                    {
                        "run_id": "RUN-TEST-060",
                        "role": "generator",
                        "argv": command,
                        "seed": 7,
                        "curve_id": None,
                        "parameters": {},
                        "timeout_seconds": 5,
                        "predecessor": None,
                    }
                ],
            }
            self._write_specification(experiment_dir, specification)
            validate_record(experiment_dir / "specification.json", REPO_ROOT)

            with self.assertRaisesRegex(RecordValidationError, "argv"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-060",
                    command=[*command, "unexpected"],
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=False,
                )
            with self.assertRaisesRegex(RecordValidationError, "forbids allow_dirty"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-060",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=True,
                )
            with patch.object(
                runner_module,
                "_git_state",
                return_value={"commit": "0" * 40, "dirty": True},
            ), self.assertRaisesRegex(RecordValidationError, "working tree is dirty"):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-060",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=False,
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

    def test_execution_plan_graph_and_predecessor_sha_linkage(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            predecessor_path = (
                experiment_dir / "runs" / "RUN-TEST-070" / "raw-result.json"
            )
            generator_command = self._valid_command()
            verifier_program = (
                "import hashlib, json, sys; raw = open(sys.argv[1], 'rb').read(); "
                "print(json.dumps({'valid': True, 'input': "
                "{'sha256': hashlib.sha256(raw).hexdigest()}}))"
            )
            verifier_command = [
                sys.executable,
                "-c",
                verifier_program,
                str(predecessor_path),
            ]
            mismatch_command = [
                sys.executable,
                "-c",
                "import json; print(json.dumps({'valid': True, "
                "'input': {'sha256': '0' * 64}}))",
            ]
            specification = self._specification()
            specification["experiment"]["budget"]["maximum_runs"] = 3
            specification["experiment"]["execution_plan"] = {
                "allow_dirty": False,
                "protocol_hashes": self._protocol_hashes(experiment_dir),
                "runs": [
                    {
                        "run_id": "RUN-TEST-070",
                        "role": "generator",
                        "argv": generator_command,
                        "seed": 7,
                        "curve_id": "toy-curve",
                        "parameters": {"phase": "generate"},
                        "timeout_seconds": 5,
                        "predecessor": None,
                    },
                    {
                        "run_id": "RUN-TEST-071",
                        "role": "verifier",
                        "argv": verifier_command,
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
                        "argv": mismatch_command,
                        "seed": 7,
                        "curve_id": "toy-curve",
                        "parameters": {"phase": "mismatch"},
                        "timeout_seconds": 5,
                        "predecessor": {
                            "run_id": "RUN-TEST-070",
                            "artifact": "raw-result.json",
                        },
                    },
                ],
            }
            self._write_specification(experiment_dir, specification)
            clean_git = {"commit": "0" * 40, "dirty": False}
            with patch.object(runner_module, "_git_state", return_value=clean_git):
                with self.assertRaisesRegex(
                    RecordValidationError, "predecessor has not completed"
                ):
                    run_experiment(
                        repo_root=REPO_ROOT,
                        experiment_dir=experiment_dir,
                        run_id="RUN-TEST-071",
                        command=verifier_command,
                        seed=7,
                        curve_id="toy-curve",
                        parameters={"phase": "verify"},
                        timeout_seconds=None,
                        allow_dirty=False,
                    )
                generator = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-070",
                    command=generator_command,
                    seed=7,
                    curve_id="toy-curve",
                    parameters={"phase": "generate"},
                    timeout_seconds=None,
                    allow_dirty=False,
                )
                generator_manifest_path = generator / "manifest.json"
                original_generator_manifest = generator_manifest_path.read_text(
                    encoding="utf-8"
                )
                invalid_generator_manifest = json.loads(original_generator_manifest)
                invalid_generator_manifest["run"]["status"] = "completed_invalid"
                invalid_generator_manifest["run"]["result"]["valid"] = False
                generator_manifest_path.write_text(
                    json.dumps(invalid_generator_manifest), encoding="utf-8"
                )
                try:
                    with self.assertRaisesRegex(
                        RecordValidationError, "predecessor is not completed_valid"
                    ):
                        run_experiment(
                            repo_root=REPO_ROOT,
                            experiment_dir=experiment_dir,
                            run_id="RUN-TEST-071",
                            command=verifier_command,
                            seed=7,
                            curve_id="toy-curve",
                            parameters={"phase": "verify"},
                            timeout_seconds=None,
                            allow_dirty=False,
                        )
                finally:
                    generator_manifest_path.write_text(
                        original_generator_manifest, encoding="utf-8"
                    )
                verifier = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-071",
                    command=verifier_command,
                    seed=7,
                    curve_id="toy-curve",
                    parameters={"phase": "verify"},
                    timeout_seconds=None,
                    allow_dirty=False,
                )
                mismatch = run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-072",
                    command=mismatch_command,
                    seed=7,
                    curve_id="toy-curve",
                    parameters={"phase": "mismatch"},
                    timeout_seconds=None,
                    allow_dirty=False,
                )

            generator_manifest = json.loads(
                (generator / "manifest.json").read_text(encoding="utf-8")
            )["run"]
            verifier_manifest = json.loads(
                (verifier / "manifest.json").read_text(encoding="utf-8")
            )["run"]
            mismatch_manifest = json.loads(
                (mismatch / "manifest.json").read_text(encoding="utf-8")
            )["run"]
            self.assertEqual(generator_manifest["status"], "completed_valid")
            self.assertEqual(verifier_manifest["status"], "completed_valid")
            self.assertEqual(mismatch_manifest["status"], "completed_invalid")
            self.assertIn(
                "input.sha256 does not match predecessor",
                mismatch_manifest["result"]["invalid_reason"],
            )

    def test_execution_plan_graph_requires_predecessor_to_appear_first(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            command = self._valid_command()
            specification = self._specification()
            specification["experiment"]["budget"]["maximum_runs"] = 2
            specification["experiment"]["execution_plan"] = {
                "allow_dirty": False,
                "protocol_hashes": self._protocol_hashes(experiment_dir),
                "runs": [
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
                ],
            }
            self._write_specification(experiment_dir, specification)
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

    def test_execution_plan_rejects_clean_protocol_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            source_path = experiment_dir / "generator.py"
            source_path.write_text(
                "import json\nprint(json.dumps({'valid': True}))\n",
                encoding="utf-8",
            )
            source_argument = source_path.relative_to(REPO_ROOT).as_posix()
            command = [sys.executable, source_argument]
            specification = self._specification()
            specification["experiment"]["execution_plan"] = {
                "allow_dirty": False,
                "protocol_hashes": self._protocol_hashes(
                    experiment_dir, source_path
                ),
                "runs": [
                    {
                        "run_id": "RUN-TEST-090",
                        "role": "generator",
                        "argv": command,
                        "seed": 7,
                        "curve_id": None,
                        "parameters": {},
                        "timeout_seconds": 5,
                        "predecessor": None,
                    }
                ],
            }
            self._write_specification(experiment_dir, specification)
            source_path.write_text(
                "import json\nprint(json.dumps({'valid': False}))\n",
                encoding="utf-8",
            )

            clean_git = {"commit": "0" * 40, "dirty": False}
            with patch.object(
                runner_module, "_git_state", return_value=clean_git
            ) as git_state, self.assertRaisesRegex(
                RecordValidationError, "protocol SHA-256 mismatch"
            ):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-090",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=False,
                )
            git_state.assert_not_called()
            self.assertFalse((experiment_dir / "runs").exists())

    def test_execution_plan_rejects_protocol_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            command = self._valid_command()
            protocol_hashes = self._protocol_hashes(experiment_dir)
            protocol_hashes.insert(
                0,
                {
                    "path": "../outside-repository.py",
                    "sha256": "0" * 64,
                },
            )
            specification = self._specification()
            specification["experiment"]["execution_plan"] = {
                "allow_dirty": False,
                "protocol_hashes": protocol_hashes,
                "runs": [
                    {
                        "run_id": "RUN-TEST-091",
                        "role": "generator",
                        "argv": command,
                        "seed": 7,
                        "curve_id": None,
                        "parameters": {},
                        "timeout_seconds": 5,
                        "predecessor": None,
                    }
                ],
            }
            self._write_specification(experiment_dir, specification)

            with patch.object(runner_module, "_git_state") as git_state, self.assertRaisesRegex(
                RecordValidationError, "parent traversal"
            ):
                run_experiment(
                    repo_root=REPO_ROOT,
                    experiment_dir=experiment_dir,
                    run_id="RUN-TEST-091",
                    command=command,
                    seed=7,
                    curve_id=None,
                    parameters={},
                    timeout_seconds=5,
                    allow_dirty=False,
                )
            git_state.assert_not_called()
            self.assertFalse((experiment_dir / "runs").exists())


if __name__ == "__main__":
    unittest.main()
