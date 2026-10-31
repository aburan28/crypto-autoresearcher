from __future__ import annotations

import sys
import json
from types import SimpleNamespace
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_solve_plan as plan


class RootlessSolvePlanTests(unittest.TestCase):
    def test_relation_trials_use_only_catalogued_prepared_files(self) -> None:
        source = Path(__file__).resolve()
        row = {"arm_key": "P29-v0001-low_x", "stratum": "P29",
               "path_index": 1, "base_rule": "low_x", "target_count": 32768}
        admission = plan.rel(source)
        prepared = {"input": source, "manifest": source, "binding": source}
        arms = {row["arm_key"]: prepared}
        with patch("prepared_worker.load_worker_catalog",
                   return_value=(source, arms)):
            trials = plan.make_trials(
                [row], ["RUN-ECTD-abcdef"], experiment_id="EXP-ECTD-abcdef",
                root_files={name: plan.rel(source) for name in ("base", "target", "verifier")},
                commitments={family: plan.rel(source) for family in ("P29", "P37")},
                admission_path="experiments/EXP-ECTD-abcdef/private-admission.json",
                collector_path=plan.rel(source), count_verifier_path=plan.rel(source),
                sage_path=sys.executable,
                prepared_catalog=source)
        self.assertEqual(len(trials), 1)
        trial = trials[0]
        argv = trial["argv"] + trial["check_argv"]
        for forbidden in ("--arm-key", "--base-root-file", "--target-root-file",
                          "--verifier-root-file", "--commitment", "private-admission"):
            self.assertNotIn(forbidden, argv)
        self.assertIn("--prepared-worker-admission", argv)
        self.assertIn("--binding", argv)
        self.assertFalse(any(path.startswith("prepared/") or path.startswith("materializer.")
                             for path in trial["artifacts"]))

    def test_matched_rho_uses_the_same_catalogued_low_x_input(self) -> None:
        source = Path(__file__).resolve()
        rows = [{"arm_key": f"P29-v0001-{arm}", "stratum": "P29",
                 "path_index": 1, "model": {"j": "0x123"}}
                for arm in plan.ARMS]
        low = {"input": source, "manifest": source, "binding": source}
        rho = plan.make_rho_trials(
            rows, [f"RUN-ECTD-{index:06x}" for index in range(10)],
            {row["arm_key"]: f"RUN-ECTD-{index:06x}"
             for index, row in enumerate(rows)}, list(range(10)),
            experiment_id="EXP-ECTD-abcdef",
            prepared_arms={rows[0]["arm_key"]: low})
        self.assertEqual(len(rho), 10)
        expected = plan.rel(source)
        for trial in rho:
            argv = trial["argv"] + trial["check_argv"]
            self.assertEqual(argv[argv.index("--input") + 1], expected)
            self.assertEqual(argv[argv.index("--manifest") + 1], expected)
            self.assertEqual(trial["depends_on"], [])
            self.assertEqual(trial["parameters"]["prepared_input_sha256"], plan.sha(source))
            self.assertNotIn("/runs/", " ".join(argv))

    def test_path_transfer_uses_catalogued_public_manifest_without_roots(self) -> None:
        rows = [
            {"arm_key": f"P29-v{index:04d}-low_x", "stratum": "P29",
             "path_index": index, "model": {"j": f"0x{index:x}"}}
            for index in (1, 2)
        ]
        with tempfile.TemporaryDirectory(prefix="transfer-plan-") as temporary:
            prepared_arms = {}
            for index in (1, 2):
                manifest = Path(temporary) / f"{index}-manifest.json"
                manifest.write_text(json.dumps({
                    "source_points_sha256": "a" * 64,
                    "source_generator": [1, 2], "source_Q": [3, 4],
                    "generator": [5, index], "Q": [7, index],
                    "target_vector_sha256": "b" * 64,
                }))
                prepared_arms.update({
                    f"P29-v{index:04d}-{arm}": {"manifest": manifest}
                    for arm in plan.ARMS})
            with patch.object(plan, "rel", side_effect=lambda path: str(path)):
                trials = plan.make_transfer_trials(
                    rows, ["RUN-ECTD-aaaaaa", "RUN-ECTD-bbbbbb"],
                    experiment_id="EXP-ECTD-abcdef",
                    relation_run_ids={},
                    prepared_arms=prepared_arms, sage_path=sys.executable)
        self.assertEqual(len(trials), 2)
        trial = trials[0]
        argv = trial["argv"] + trial["check_argv"]
        self.assertIn("--source-manifest", argv)
        self.assertIn("--endpoint-manifest", argv)
        self.assertNotIn("--verifier-root-file", argv)
        self.assertNotIn("--scalar", argv)
        self.assertEqual(trial["depends_on"], [])
        self.assertFalse(trial["parameters"]["scalar_or_seed_in_worker_argv"])

    def test_path_transfer_rejects_target_vector_drift_between_finalists(self) -> None:
        rows = [
            {"arm_key": f"P29-v{index:04d}-low_x", "stratum": "P29",
             "path_index": index, "model": {"j": f"0x{index:x}"}}
            for index in (1, 2)
        ]
        with tempfile.TemporaryDirectory(prefix="transfer-target-stream-") as temporary:
            root = Path(temporary)
            prepared_arms = {}
            for index, target_digest in ((1, "b" * 64), (2, "c" * 64)):
                for arm in plan.ARMS:
                    manifest = root / f"{index}-{arm}.json"
                    manifest.write_text(json.dumps({
                        "source_points_sha256": "a" * 64,
                        "source_generator": [1, 2], "source_Q": [3, 4],
                        "generator": [5, index], "Q": [7, index],
                        "target_vector_sha256": target_digest,
                    }))
                    prepared_arms[f"P29-v{index:04d}-{arm}"] = {"manifest": manifest}
            with patch.object(plan, "rel", side_effect=lambda path: str(path)):
                with self.assertRaisesRegex(ValueError, "do not share the stratum target vector"):
                    plan.make_transfer_trials(
                        rows, ["RUN-ECTD-aaaaaa", "RUN-ECTD-bbbbbb"],
                        experiment_id="EXP-ECTD-abcdef", relation_run_ids={},
                        prepared_arms=prepared_arms, sage_path=sys.executable)

    def test_approved_solve_plan_removes_private_root_and_commitment_bindings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rootless-solve-") as tmp:
            root = Path(tmp)
            (root / "experiments/EXP-ECTD-abcdef").mkdir(parents=True)

            def rel_tmp(path: Path) -> str:
                return path.resolve().relative_to(root.resolve()).as_posix()

            def put(name: str, data: str) -> Path:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(data)
                return path

            spec_path = put("experiments/EXP-ECTD-abcdef/specification.yaml", "spec\n")
            decision_path = put("decisions/decision.yaml", "coordinator_decision: {}\n")
            schedule_path = put("schedule/discovery-arms.jsonl", "schedule\n")
            schedule_manifest = put("schedule/manifest.json", "manifest\n")
            schedule_verification = put("schedule/verification.json", "verified\n")
            secondary_arms = put("schedule/p29-secondary-floor-arms.jsonl", "secondary\n")
            secondary_manifest = put("schedule/p29-secondary-floor-manifest.json", "secondary manifest\n")
            secondary_verification = put("schedule/p29-secondary-floor-verification.json", "secondary verified\n")
            graph_manifest = put("study/manifest-v2.json", "graph manifest\n")
            verify_source = put("study/preparation/verify_prepared_graph.py", "verifier source\n")
            source_map = {rel_tmp(verify_source): plan.sha(verify_source)}
            selection_path = put("selection.json", "{}\n")
            analysis_path = put("analysis.json", "{}\n")
            roots = {name: put(f"roots/{name}.dat", name) for name in ("base", "target", "verifier")}
            prior_roots = {name: put(f"prior/confirm-{name}.dat", name if name != "target" else "confirm")
                           for name in ("base", "target", "verifier")}
            discovery_roots = {name: put(f"prior/discovery-{name}.dat", name if name != "target" else "discovery")
                               for name in ("base", "target", "verifier")}
            prior_discovery = put("prior/discovery.json", json.dumps({
                "schema": "ectd.graph-study-admission.v1", "status": "approved",
                "execution_stage": 0, "experiment_id": "EXP-ECTD-abcdef",
                "root_files": {name: rel_tmp(path) for name, path in discovery_roots.items()}}))
            prior_confirmation = put("prior/confirmation.json", json.dumps({
                "schema": "ectd.graph-study-admission.v1", "status": "approved",
                "approved_by": "coordinator", "execution_stage": 1,
                "experiment_id": "EXP-ECTD-abcdef",
                "root_files": {name: rel_tmp(path) for name, path in prior_roots.items()},
                "selection_path": rel_tmp(selection_path),
                "selection_sha256": plan.sha(selection_path),
                "prior_admission_path": rel_tmp(prior_discovery),
                "prior_admission_sha256": plan.sha(prior_discovery)}))
            collector = put("bin/collector", "collector")
            count_verifier = put("bin/count", "count")
            sage = put("bin/sage", "sage")
            binary_candidate = {
                "collector": {"path": rel_tmp(collector), "sha256": plan.sha(collector)},
                "count_verifier": {"path": rel_tmp(count_verifier), "sha256": plan.sha(count_verifier)},
                "sage": {"path": rel_tmp(sage), "sha256": plan.sha(sage)},
            }
            commitment_files = {family: put(f"commitments/{family}.json", family)
                                for family in ("P29", "P37")}
            commitments = {}
            strata = {}
            for family, commitment in commitment_files.items():
                item = {"path": rel_tmp(commitment), "sha256": plan.sha(commitment),
                        "graph_sha256": "a" * 64}
                item.update({name + "_root_sha256": plan.sha(roots[name])
                             for name in ("base", "target", "verifier")})
                commitments[family] = item
                strata[family] = {"commitment_path": item["path"],
                                  "commitment_sha256": item["sha256"],
                                  "graph_sha256": item["graph_sha256"]}
                strata[family].update({name + "_root_sha256": item[name + "_root_sha256"]
                                       for name in ("base", "target", "verifier")})
            seed_file = put("seeds/rho.txt", "\n".join(map(str, range(10))) + "\n")
            decision = {"id": "DEC-TEST", "decision": "approve"}
            admission = {
                "schema": "ectd.graph-study-admission.v1", "status": "approved",
                "approved_by": "coordinator", "execution_stage": 2,
                "experiment_id": "EXP-ECTD-abcdef", "decision_id": "DEC-TEST",
                "decision_path": rel_tmp(decision_path), "decision_sha256": plan.sha(decision_path),
                "specification_path": rel_tmp(spec_path), "specification_sha256": plan.sha(spec_path),
                "task_id": "TASK-test", "source_commit": "a" * 40, "source_sha256": source_map,
                "output_prefix": "experiments/EXP-ECTD-abcdef/runs",
                "schedule": {
                    "arms_sha256": plan.sha(schedule_path),
                    "manifest_sha256": plan.sha(schedule_manifest),
                    "verification_sha256": plan.sha(schedule_verification),
                    "graph_manifest_sha256": plan.sha(graph_manifest),
                    "arm_count": 8206, "target_probes": 60889088,
                    "secondary_controls": {
                        "arms_sha256": plan.sha(secondary_arms),
                        "manifest_sha256": plan.sha(secondary_manifest),
                        "verification_sha256": plan.sha(secondary_verification),
                        "arm_count": 4, "target_probes": 32768}},
                "selection_path": rel_tmp(selection_path), "selection_sha256": plan.sha(selection_path),
                "finalist_analysis_path": rel_tmp(analysis_path),
                "finalist_analysis_sha256": plan.sha(analysis_path),
                "prior_admission_path": rel_tmp(prior_confirmation),
                "prior_admission_sha256": plan.sha(prior_confirmation),
                "root_files": {name: rel_tmp(path) for name, path in roots.items()},
                "binaries": {
                    "collector_path": binary_candidate["collector"]["path"],
                    "collector_sha256": binary_candidate["collector"]["sha256"],
                    "count_verifier_path": binary_candidate["count_verifier"]["path"],
                    "count_verifier_sha256": binary_candidate["count_verifier"]["sha256"],
                    "sage_path": binary_candidate["sage"]["path"],
                    "sage_sha256": binary_candidate["sage"]["sha256"]},
                "strata": strata,
            }
            admission_path = put("admission.json", json.dumps(admission))
            worker_admission = put("worker-admission.json", "rootless admission\n")
            catalog = put("catalog.json", "catalog\n")
            rows = [{"arm_key": f"P29-v0001-{arm}", "stratum": "P29",
                     "path_index": 1, "model": {"j": "0x123"}}
                    for arm in plan.ARMS]
            relation = [{"id": row["arm_key"], "run_id": f"RUN-ECTD-{index:06x}",
                         "memory_mb": 4096, "watchdog_seconds": 1830,
                         "parameters": {"stage": "solve", "stratum": "P29"},
                         "argv": ["rootless"]}
                        for index, row in enumerate(rows)]
            rho = [{"id": f"P29-v0001-rho-{i:02d}",
                    "run_id": f"RUN-ECTD-{i + 10:06x}", "memory_mb": 2048,
                    "watchdog_seconds": 1830,
                    "parameters": {"repetition": i, "seed": i}}
                   for i in range(10)]
            transfer = [{"id": "P29-v0001-path-transfer",
                         "run_id": "RUN-ECTD-000014", "memory_mb": 8192,
                         "watchdog_seconds": 1830,
                         "parameters": {"phase": "path_transfer"},
                         "argv": ["rootless"]}]
            candidate = {
                "schema": "crypto.autoresearch.trial_plan.v1", "candidate_only": True,
                "approval_required": True, "experiment_id": "EXP-ECTD-abcdef",
                "task_id": "TASK-test", "specification": rel_tmp(spec_path),
                "specification_sha256": plan.sha(spec_path), "source_commit": "a" * 40,
                "source_sha256": source_map, "schedule_sha256": plan.sha(schedule_path),
                "selection": {"path": rel_tmp(selection_path), "sha256": plan.sha(selection_path)},
                "finalist_analysis": {"path": rel_tmp(analysis_path), "sha256": plan.sha(analysis_path)},
                "prior_confirmation_admission": {"path": rel_tmp(prior_confirmation),
                                                  "sha256": plan.sha(prior_confirmation)},
                "prior_discovery_admission": {"path": rel_tmp(prior_discovery),
                                               "sha256": plan.sha(prior_discovery)},
                "root_files": {name: {"path": rel_tmp(path), "sha256": plan.sha(path)}
                               for name, path in roots.items()},
                "commitments": commitments, "binaries": binary_candidate,
                "rho_seed_file": {"path": rel_tmp(seed_file), "sha256": plan.sha(seed_file)},
                "relation_trial_count": len(relation), "transfer_trial_count": len(transfer),
                "rho_trial_count": len(rho),
                "trials": relation + transfer + rho,
            }
            candidate_path = put("candidate.json", json.dumps(candidate))
            output_path = root / "experiments/EXP-ECTD-abcdef/approved-plan.json"
            empty_arms = {row["arm_key"]: {"input": schedule_path,
                                            "manifest": schedule_path,
                                            "binding": schedule_path} for row in rows}
            with (patch.object(plan, "ROOT", root),
                  patch.object(plan, "STUDY", root / "study"),
                  patch.object(plan, "SOURCE_PATHS", ()),
                  patch.object(plan, "SCHEDULE_DIR", schedule_path.parent),
                  patch("study_admission.validate_approval_fields",
                        return_value=(decision, {}, 2)),
                  patch.dict(sys.modules, {
                      "build_confirmation_plan": SimpleNamespace(SOURCE_PATHS=()),
                      "execute_graph_prepared": SimpleNamespace(
                          source_paths=lambda: {}, check_frozen_sources=lambda *args: None)}),
                  patch("prepared_worker.load_worker_catalog",
                        return_value=(worker_admission, empty_arms)),
                  patch.object(plan, "finalist_rows", return_value=rows),
                  patch.object(plan, "make_trials", return_value=relation),
                  patch.object(plan, "make_transfer_trials", return_value=transfer),
                  patch.object(plan, "make_rho_trials", return_value=rho)):
                result = plan.build_approved(candidate_path, admission_path, decision_path,
                                             spec_path, output_path, catalog)
            self.assertEqual(result["status"], "built")
            body = json.loads(output_path.read_text())
            self.assertNotIn("root_files", body)
            self.assertNotIn("commitments", body)
            self.assertNotIn("prior_confirmation_admission", body)
            self.assertNotIn("prior_discovery_admission", body)
            serialized = json.dumps(body)
            for path in roots.values():
                self.assertNotIn(rel_tmp(path), serialized)
            for path in commitment_files.values():
                self.assertNotIn(rel_tmp(path), serialized)
            self.assertEqual(body["prepared_catalog_sha256"], plan.sha(catalog))
            self.assertEqual(body["stage_admission"]["sha256"], plan.sha(admission_path))


if __name__ == "__main__":
    unittest.main()
