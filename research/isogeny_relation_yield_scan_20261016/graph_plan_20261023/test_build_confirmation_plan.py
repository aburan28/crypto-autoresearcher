"""Controls for compiling the deterministic held-out confirmation workload."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY / "graph_input_schedule_20261023"))
sys.path.insert(0, str(HERE))
from build_confirmation_plan import (  # noqa: E402
    CHECKER, DRIVER, ROOT, build_approved, make_trials, rel, selected_rows, sha,
)
sys.path.insert(0, str(ROOT / "tools"))
import experiment_execution  # noqa: E402

SCHEDULE = STUDY / "graph_schedule_20261023/discovery-arms.jsonl"


class ConfirmationPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(line) for line in SCHEDULE.read_text().splitlines()]
        cls.by_key = {row["arm_key"]: row for row in cls.rows}
        cls.selection = {
            "schema": "ectd.graph-discovery-selection-candidate/v1",
            "status": "selected_from_validated_discovery", "discovery_arms_checked": 8206,
            "schedule_sha256": sha(SCHEDULE),
            "strata": {},
        }
        for family in ("P29", "P37"):
            vertices = [0]
            cls.selection["strata"][family] = {
                "selected_vertices": [{"index": index} for index in vertices],
                "confirmation_arm_keys": [f"{family}-v{index:04d}-{arm}"
                                           for index in vertices
                                           for arm in ("low_x", "mid_x", "random_x")],
            }

    def test_exact_selected_arm_coverage_and_stage_quota(self):
        rows = selected_rows(self.selection, SCHEDULE)
        self.assertEqual(len(rows), 6)
        self.assertEqual({row["base_rule"] for row in rows}, {"low_x", "mid_x", "random_x"})
        self.assertTrue(all(self.by_key[row["arm_key"]] == row for row in rows))
        self.assertEqual(len({row["arm_key"] for row in rows}), len(rows))

    def test_missing_arm_and_duplicate_vertex_are_rejected(self):
        changed = json.loads(json.dumps(self.selection))
        changed["strata"]["P29"]["confirmation_arm_keys"].pop()
        with self.assertRaisesRegex(ValueError, "exact selected three-arm set"):
            selected_rows(changed, SCHEDULE)
        changed = json.loads(json.dumps(self.selection))
        changed["strata"]["P29"]["selected_vertices"].append({"index": 0})
        with self.assertRaisesRegex(ValueError, "exact selected three-arm set"):
            selected_rows(changed, SCHEDULE)

    def test_trials_bind_stage_quota_resources_and_run_ids(self):
        rows = selected_rows(self.selection, SCHEDULE)
        run_ids = [f"RUN-ECTD-{value:06x}" for value in range(1, len(rows) + 1)]
        trials = make_trials(rows, run_ids, experiment_id="EXP-ECTD-abcdef",
                             root_files={"base": "base", "target": "target", "verifier": "verifier"},
                             commitments={"P29": "p29", "P37": "p37"},
                             admission_path="admission", collector="collector",
                             count_verifier="count")
        self.assertEqual(len(trials), 6)
        for trial in trials:
            self.assertEqual(trial["parameters"], {
                "stage": "confirmation", "stratum": trial["id"][:3],
                "index": int(trial["id"].split("-v")[1][:4]),
                "arm": trial["id"].split("-")[-1], "target_count": 32768})
            self.assertIn("--stage", trial["argv"])
            self.assertEqual(trial["watchdog_seconds"], 1830)

    def test_candidate_plan_schema_is_readiness_valid_but_not_executable(self):
        rows = selected_rows(self.selection, SCHEDULE)[:3]
        trials = make_trials(rows, [f"RUN-ECTD-{value:06x}" for value in (1, 2, 3)],
                             experiment_id="placeholder",
                             root_files={"base": "root/base", "target": "root/target",
                                         "verifier": "root/verifier"},
                             commitments={"P29": "commit/p29", "P37": "commit/p37"},
                             admission_path="experiments/placeholder/admission.json",
                             collector="bin/collector", count_verifier="bin/count")
        with tempfile.TemporaryDirectory(prefix="ectd-confirm-candidate-",
                                         dir=ROOT / "experiments") as tmp:
            exp = Path(tmp)
            experiment_id = exp.name
            spec = exp / "specification.yaml"
            spec_doc = {"experiment": {"id": experiment_id,
                "status": "review_required", "frozen": True,
                "approved_by": None, "execution_authorized": False}}
            spec.write_text(json.dumps(spec_doc))
            source_hashes = {rel(path): sha(path) for path in (DRIVER, CHECKER)}
            plan = {"schema": "crypto.autoresearch.trial_plan.v1",
                    "experiment_id": experiment_id, "task_id": "TASK-ECTD-candidate",
                    "candidate_only": True, "approval_required": True, "frozen": True,
                    "stop_on_invalid_output": True,
                    "specification": rel(spec), "specification_sha256": sha(spec),
                    "queue": f"experiments/{experiment_id}/queue.json",
                    "source_sha256": source_hashes, "trials": trials}
            path = exp / "candidate-confirmation-trial-plan.json"
            path.write_text(json.dumps(plan))
            loaded = experiment_execution.load_plan(ROOT, path,
                                                      allow_preapproval_candidate=True)
            self.assertEqual(len(loaded["trials"]), 3)
            with self.assertRaisesRegex(experiment_execution.ExecutionError,
                                        "candidate-only trial plans cannot execute"):
                experiment_execution.load_plan(ROOT, path)

    def test_approved_plan_conversion_requires_matching_stage_one_bindings(self):
        decision_id = "DEC-20261023-a1b2c3"
        with tempfile.TemporaryDirectory(prefix="ectd-confirm-approved-",
                                         dir=ROOT / "experiments") as tmp:
            exp = Path(tmp)
            experiment_id = exp.name
            spec_path = exp / "specification.yaml"
            spec_doc = {"experiment": {"id": experiment_id, "status": "approved",
                "approved_by": decision_id, "frozen": True, "execution_authorized": True,
                "execution_authorized_stages": [1]}}
            spec_path.write_text(json.dumps(spec_doc))
            decision_path = exp / "decision.yaml"
            decision_doc = {"coordinator_decision": {"id": decision_id,
                "decided_by": "coordinator", "decision": "approve",
                "mode": "design_experiment_approval", "approved_by": decision_id,
                "target_ids": [experiment_id],
                "official_transitions": {"execution_authorized_stages": [1]}}}
            decision_path.write_text(json.dumps(decision_doc))
            selection_path = exp / "selection.json"
            selection_path.write_text(json.dumps(self.selection) + "\n")
            prior_path = exp / "prior-admission.json"
            prior_path.write_text('{"admission":true}\n')
            roots, commitments, binaries = {}, {}, {}
            for name in ("base", "target", "verifier", "collector", "count"):
                path = exp / f"{name}.bin"
                path.write_bytes((name + "\n").encode())
                if name in ("base", "target", "verifier"):
                    roots[name] = {"path": rel(path), "sha256": sha(path)}
                elif name == "collector":
                    binaries["collector"] = {"path": rel(path), "sha256": sha(path)}
                else:
                    binaries["count_verifier"] = {"path": rel(path), "sha256": sha(path)}
            for family in ("P29", "P37"):
                path = exp / f"commitment-{family}.json"
                path.write_text(f'{{"family":"{family}"}}\n')
                commitments[family] = {"path": rel(path), "sha256": sha(path),
                    "graph_sha256": "a" * 64,
                    "base_root_sha256": "b" * 64, "target_root_sha256": "c" * 64,
                    "verifier_root_sha256": "d" * 64}
            source_hashes = {rel(path): sha(path) for path in (DRIVER, CHECKER)}
            trial_rows = selected_rows(self.selection, SCHEDULE)
            run_ids = [f"RUN-ECTD-{value:06x}" for value in range(1, len(trial_rows) + 1)]
            trials = make_trials(trial_rows, run_ids,
                experiment_id=experiment_id,
                root_files={name: value["path"] for name, value in roots.items()},
                commitments={family: item["path"] for family, item in commitments.items()},
                admission_path=f"experiments/{experiment_id}/graph-study-admission-confirmation.json",
                collector=binaries["collector"]["path"],
                count_verifier=binaries["count_verifier"]["path"])
            candidate = {"schema": "crypto.autoresearch.trial_plan.v1",
                "experiment_id": experiment_id, "task_id": "TASK-ECTD-a1b2c3",
                "candidate_only": True, "approval_required": True, "frozen": True,
                "specification": rel(spec_path), "source_commit": "1" * 40,
                "source_sha256": source_hashes, "schedule_sha256": sha(SCHEDULE),
                "selection": {"path": rel(selection_path), "sha256": sha(selection_path)},
                "prior_discovery_admission": {"path": rel(prior_path), "sha256": sha(prior_path)},
                "root_files": roots, "commitments": commitments, "binaries": binaries,
                "queue": f"experiments/{experiment_id}/queue.json", "trials": trials}
            candidate_path = exp / "candidate-confirmation-trial-plan.json"
            candidate_path.write_text(json.dumps(candidate))
            admission = {"schema": "ectd.graph-study-admission.v1", "status": "approved",
                "approved_by": "coordinator", "experiment_id": experiment_id,
                "execution_stage": 1, "decision_id": decision_id,
                "decision_path": rel(decision_path), "decision_sha256": sha(decision_path),
                "specification_path": rel(spec_path), "specification_sha256": sha(spec_path),
                "task_id": candidate["task_id"], "source_commit": candidate["source_commit"],
                "source_sha256": source_hashes,
                "output_prefix": f"experiments/{experiment_id}/runs",
                "selection_path": rel(selection_path), "selection_sha256": sha(selection_path),
                "prior_admission_path": rel(prior_path), "prior_admission_sha256": sha(prior_path),
                "root_files": {name: value["path"] for name, value in roots.items()},
                "binaries": {"collector_path": binaries["collector"]["path"],
                    "collector_sha256": binaries["collector"]["sha256"],
                    "count_verifier_path": binaries["count_verifier"]["path"],
                    "count_verifier_sha256": binaries["count_verifier"]["sha256"]},
                "strata": {family: {"commitment_path": item["path"],
                    "commitment_sha256": item["sha256"], "graph_sha256": item["graph_sha256"],
                    "base_root_sha256": item["base_root_sha256"],
                    "target_root_sha256": item["target_root_sha256"],
                    "verifier_root_sha256": item["verifier_root_sha256"]}
                    for family, item in commitments.items()}}
            admission_path = exp / "admission.json"
            admission_path.write_text(json.dumps(admission))
            out = exp / "confirmation-trial-plan.json"
            result = build_approved(candidate_path, admission_path, decision_path,
                                    spec_path, out)
            plan = json.loads(out.read_text())
            self.assertEqual(result["status"], "built")
            self.assertEqual(plan["approved_by"], decision_id)
            self.assertNotIn("candidate_only", plan)
            self.assertEqual(plan["stage_admission"]["sha256"], sha(admission_path))
            loaded = experiment_execution.load_plan(ROOT, out)
            self.assertEqual(loaded["approved_by"], decision_id)
            self.assertEqual(len(loaded["trials"]), 6)
            self.assertEqual(loaded["trials"][0]["parameters"]["target_count"], 32768)


if __name__ == "__main__":
    unittest.main(verbosity=2)
