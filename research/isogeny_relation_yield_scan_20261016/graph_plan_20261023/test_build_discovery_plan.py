"""Plan-shape controls; never allocate research RUN IDs or launch trials."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import tempfile
import unittest

import build_discovery_plan as plan

ROOT = plan.ROOT
sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution  # noqa: E402


class DiscoveryPlanTests(unittest.TestCase):
    def test_all_fixed_arms_have_one_trial_and_exact_quota(self) -> None:
        rows = plan.load_rows()
        run_ids = [f"RUN-ECTD-{index:06x}" for index in range(len(rows))]
        trials = plan.make_trials(
            rows, run_ids, experiment_id="EXP-ECTD-abcdef",
            root_files={"base": "roots/base.hex", "target": "roots/discovery.hex",
                        "verifier": "roots/verifier.hex"},
            commitments={"P29": "roots/p29-commitment.json",
                         "P37": "roots/p37-commitment.json"},
            admission_path="experiments/EXP-ECTD-abcdef/admission.json",
            collector="build/collector", count_verifier="build/count_verify")
        self.assertEqual(len(trials), 8210)
        self.assertEqual(len({trial["id"] for trial in trials}), 8210)
        self.assertEqual(len({trial["run_id"] for trial in trials}), 8210)
        self.assertEqual(sum(trial["id"].startswith("P29-E") for trial in trials), 4)
        self.assertTrue(all(trial["memory_mb"] == (4096 if trial["id"].startswith("P29") else 8192)
                            for trial in trials))
        self.assertTrue(all("--arm-key" in trial["argv"] for trial in trials))
        with_reference = [trial for trial in trials if trial["depends_on"]]
        self.assertTrue(all("--reference-run-dir" in trial["check_argv"]
                            for trial in with_reference))
        self.assertEqual(len(with_reference), sum(bool(row.get("control_reference")) for row in rows))
        for row, trial in zip(rows, trials):
            quota = 8192 if row["stratum"] == "P29" else 2048
            self.assertEqual(trial["id"], row["arm_key"])
            self.assertIn(str(quota), trial["note"])

    def test_run_id_file_refuses_wrong_count_and_collisions(self) -> None:
        with self.assertRaises(ValueError):
            plan.read_run_ids(Path(__file__), 8210)
        with self.assertRaises(ValueError):
            plan.read_run_ids(Path(__file__), 1)

    def test_full_plan_is_accepted_by_repository_execution_loader(self) -> None:
        rows = plan.load_rows()
        run_ids = [f"RUN-ECTD-{index:06x}" for index in range(len(rows))]
        experiment_id = "EXP-ECTD-plan-control"
        trials = plan.make_trials(
            rows, run_ids, experiment_id=experiment_id,
            root_files={"base": "roots/base.hex", "target": "roots/discovery.hex",
                        "verifier": "roots/verifier.hex"},
            commitments={"P29": "roots/p29-commitment.json",
                         "P37": "roots/p37-commitment.json"},
            admission_path=f"experiments/{experiment_id}/admission.json",
            collector="build/collector", count_verifier="build/count_verify")
        with tempfile.TemporaryDirectory(prefix=f"{experiment_id}-", dir=ROOT / "experiments") as tmp:
            exp_dir = Path(tmp)
            current_id = exp_dir.name
            specification = exp_dir / "specification.yaml"
            specification.write_text(
                "experiment:\n"
                f"  id: {current_id}\n"
                "  status: approved\n"
                "  approved_by: DEC-20261023-a1b2c3\n"
                "  frozen: true\n"
                "  execution_authorized: true\n")
            queue = exp_dir / "implementation" / "queue.json"
            queue.parent.mkdir()
            queue.write_text("{}\n")
            plan_doc = {
                "schema": "crypto.autoresearch.trial_plan.v1",
                "experiment_id": current_id,
                "task_id": "TASK-20261023-a1b2c3",
                "approved_by": "DEC-20261023-a1b2c3",
                "specification": specification.relative_to(ROOT).as_posix(),
                "specification_sha256": plan.sha(specification),
                "queue": queue.relative_to(ROOT).as_posix(),
                "frozen": True,
                "stop_on_invalid_output": True,
                "source_sha256": {plan.rel(path): plan.sha(path) for path in plan.SOURCE_PATHS},
                "trials": trials,
            }
            trial_plan = exp_dir / "trial-plan.json"
            trial_plan.write_text(json.dumps(plan_doc))
            loaded = experiment_execution.load_plan(ROOT, trial_plan)
            self.assertEqual(len(loaded["trials"]), 8210)
            self.assertIs(loaded["stop_on_invalid_output"], True)

    def test_full_candidate_plan_is_ready_but_non_executable(self) -> None:
        rows = plan.load_rows()
        run_ids = [f"RUN-ECTD-{index:06x}" for index in range(len(rows))]
        experiment_id = "EXP-ECTD-candidate-control"
        trials = plan.make_trials(
            rows, run_ids, experiment_id=experiment_id,
            root_files={"base": "roots/base.hex", "target": "roots/discovery.hex",
                        "verifier": "roots/verifier.hex"},
            commitments={"P29": "roots/p29-commitment.json",
                         "P37": "roots/p37-commitment.json"},
            admission_path=f"experiments/{experiment_id}/graph-study-admission.json",
            collector="build/collector", count_verifier="build/count_verify")
        with tempfile.TemporaryDirectory(prefix=f"{experiment_id}-", dir=ROOT / "experiments") as tmp:
            exp_dir = Path(tmp)
            current_id = exp_dir.name
            specification = exp_dir / "specification.yaml"
            specification.write_text(
                "experiment:\n"
                f"  id: {current_id}\n"
                "  status: review_required\n"
                "  frozen: true\n"
                "  execution_authorized: false\n")
            queue = exp_dir / "implementation" / "queue.json"
            queue.parent.mkdir()
            queue.write_text("{}\n")
            candidate = {
                "schema": "crypto.autoresearch.trial_plan.v1",
                "experiment_id": current_id,
                "task_id": "TASK-20261023-a1b2c3",
                "candidate_only": True,
                "approval_required": True,
                "stop_on_invalid_output": True,
                "specification": specification.relative_to(ROOT).as_posix(),
                "specification_sha256": plan.sha(specification),
                "queue": queue.relative_to(ROOT).as_posix(),
                "frozen": True,
                "source_sha256": {plan.rel(path): plan.sha(path) for path in plan.SOURCE_PATHS},
                "trials": trials,
            }
            candidate_path = exp_dir / "candidate-trial-plan.json"
            candidate_path.write_text(json.dumps(candidate))
            loaded = experiment_execution.load_plan(
                ROOT, candidate_path, allow_preapproval_candidate=True)
            self.assertEqual(len(loaded["trials"]), 8210)
            self.assertIs(loaded["stop_on_invalid_output"], True)
            with self.assertRaises(experiment_execution.ExecutionError):
                experiment_execution.load_plan(ROOT, candidate_path)


if __name__ == "__main__":
    unittest.main()
