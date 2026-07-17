from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from crypto_autoresearcher.records import RecordValidationError, find_repo_root
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

    def test_run_is_captured_and_duplicate_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            experiment_dir = Path(temporary) / "EXP-TEST-001"
            experiment_dir.mkdir()
            (experiment_dir / "specification.json").write_text(
                json.dumps(self._specification()), encoding="utf-8"
            )
            command = [
                sys.executable,
                "-c",
                "import json; print(json.dumps({'valid': True, 'summary': {'answer': 42}}))",
            ]
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
                (experiment_dir / "specification.json").write_text(
                    json.dumps(self._specification()), encoding="utf-8"
                )
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


if __name__ == "__main__":
    unittest.main()
