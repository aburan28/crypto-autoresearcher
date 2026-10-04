"""Small Git fixtures for source-pinned, conservative coverage discovery."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pending_idea_coverage as coverage


I1 = "IDEA-20260801-002"  # A valid legacy three-digit identifier.
I2 = "IDEA-20260907-abc123"
H1 = "H-ECDLP-abc123"
E1 = "EXP-ECDLP-abc123"
E2 = "EXP-PAIR-abc123"


class CoverageFixtures(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_COUNT": "0"}
        self.git("init", "-q")
        self.write(coverage.POLICY_PATH, {
            "version": 1, "ecc_areas": ["ECDLP", "PAIR"],
            "excluded_areas": {"CLGRP": "Class group target, explicitly excluded."},
        })
        # Use the real canonical classifier, committed into each tiny fixture.
        self.write(coverage.CLASSIFIER_PATH,
                   Path(__file__).with_name("ecc_priority.py").read_text())
        self.write(coverage.REGISTRY_PATH,
                   {"schema": "schema-supersession-registry-v1", "records": []})

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), "-c", "core.hooksPath=/dev/null",
             "-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
             "-c", "user.email=fixture@example.invalid", *args], env=self.env,
            stderr=subprocess.PIPE).decode().strip()

    def write(self, path, document):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document if isinstance(document, str) else
                          json.dumps(document) if str(path).endswith(".json") else
                          yaml.safe_dump(document, sort_keys=False))
        return target

    def commit(self):
        self.git("add", "--", ".")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def idea(self, iid=I1, directory="proposals", **fields):
        return self.write(f"ledger/{directory}/{iid}.yaml", {
            "idea": {"id": iid, "question_id": "RQ-ECDLP-001", **fields}})

    def hypothesis(self, **fields):
        return self.write(f"ledger/hypotheses/{H1}.yaml", {
            "hypothesis": {"id": H1, **fields}})

    def experiment(self, eid=E1, filename="specification.yaml", **fields):
        return self.write(f"experiments/{eid}/{filename}", {
            "experiment": {"id": eid, "hypothesis_id": H1, "version": 1, **fields}})

    def queue(self, tasks, filename="implementation_queue.json", schema=coverage.QUEUE_SCHEMA):
        return self.write(f"coordination/fixture/{filename}", {"schema": schema, "tasks": tasks})

    def run_inventory(self, commit="HEAD", **kwargs):
        return coverage.build_inventory(self.repo, commit, **kwargs)

    def row(self, report, iid=I1):
        return next(r for r in report["ideas"] if r["id"] == iid)

    def test_both_directories_and_all_lifecycle_states_are_retained(self):
        self.idea(status="proposed")
        self.idea(I2, "ideas", status="withdrawn")
        self.commit()
        report = self.run_inventory()
        self.assertEqual(report["summary"]["proposal_documents"], 2)
        self.assertEqual(report["summary"]["explicit_proposed"], 1)
        self.assertEqual(self.row(report, I2)["recorded_status"], "withdrawn")
        self.assertIn("ledger/ideas/", self.row(report, I2)["original_path"])
        self.assertFalse(report["summary"]["completion_verified"])

    def test_absent_status_and_closure_disposition_do_not_become_proposed(self):
        self.idea(disposition="confirmed_scoped_residual_closed")
        self.commit()
        report = self.run_inventory()
        row = self.row(report)
        self.assertFalse(row["status_present"])
        self.assertIsNone(row["recorded_status"])
        self.assertEqual(row["recorded_disposition"], "confirmed_scoped_residual_closed")
        self.assertEqual(report["summary"]["explicit_proposed"], 0)
        self.assertEqual(row["lifecycle_audit"], "missing_status_requires_lifecycle_audit")
        self.assertNotEqual(row["coverage"], "needs_design")

    def test_policy_and_records_are_read_from_commit_not_dirty_tree(self):
        original = self.idea(status="proposed")
        self.idea(I2, question_id="RQ-CLGRP-001", status="proposed")
        pinned = self.commit()
        self.write(coverage.POLICY_PATH, {"ecc_areas": [], "excluded_areas": {"ECDLP": "dirty"}})
        self.write(coverage.CLASSIFIER_PATH, "raise RuntimeError('dirty classifier must not execute')\n")
        original.write_text("idea: {id: WRONG, status: withdrawn}\n")
        report = self.run_inventory(pinned)
        self.assertEqual(report["source_commit"], pinned)
        self.assertEqual(self.row(report)["classification"], "ecc")
        self.assertEqual(self.row(report)["recorded_status"], "proposed")
        self.assertEqual(self.row(report, I2)["classification"], "non_ecc")
        for path in (coverage.CLASSIFIER_PATH, coverage.POLICY_PATH):
            manifest = next(i for i in report["input_manifest"] if i["path"] == path)
            self.assertNotEqual(manifest["sha256"], coverage.sha256((self.repo / path).read_bytes()))

    def test_unclassified_area_and_parse_gap_remain_visible(self):
        self.idea(question_id="RQ-UNASSIGNED-001", status="proposed")
        self.idea(I2, question_id="SG-ECDLP-002", status="proposed")
        self.write("ledger/ideas/broken.yaml", "idea: [\n")
        self.write(f"experiments/{E1}/specification.yaml", "experiment: [\n")
        self.commit()
        report = self.run_inventory()
        self.assertEqual(self.row(report)["classification"], "unclassified")
        self.assertEqual(self.row(report, I2)["classification"], "unclassified")
        self.assertEqual(len(report["ideas"]), 3)
        unresolved = next(r for r in report["ideas"] if r["id"] is None)
        self.assertEqual(unresolved["coverage"], "unresolved_record")
        errors = {d["path"] for d in report["diagnostics"] if d["code"] == "parse_error"}
        self.assertIn("ledger/ideas/broken.yaml", errors)
        self.assertIn(f"experiments/{E1}/specification.yaml", errors)
        self.assertTrue(report["summary"]["discovery_has_gaps"])

    def test_replacement_preserves_hash_paths_and_legacy_source_alias(self):
        old_id = "IDEA-ISO-7f3e2d"
        old_path = f"ledger/proposals/{old_id}.yaml"
        new_path = "ledger/corrections/schema-supersessions/fixture/idea.v2.yaml"
        old = self.write(old_path, {"idea": {"id": old_id, "status": "proposed"}})
        new = self.write(new_path, {"idea": {"id": I1, "status": "proposed", "question_id": "RQ-ECDLP-001"}})
        self.write(coverage.REGISTRY_PATH, {"schema": "schema-supersession-registry-v1", "records": [{
            "kind": "ledger", "superseded_path": old_path,
            "superseded_sha256": coverage.sha256(old.read_bytes()), "superseding_path": new_path,
            "superseding_sha256": coverage.sha256(new.read_bytes()), "replacement_id": I1,
        }]})
        self.hypothesis(derived_from_idea=old_id)
        self.commit()
        report = self.run_inventory()
        row = self.row(report)
        self.assertEqual(row["original_path"], old_path)
        self.assertEqual(row["effective_path"], new_path)
        self.assertEqual(row["original_sha256"], coverage.sha256(old.read_bytes()))
        self.assertEqual(row["effective_sha256"], coverage.sha256(new.read_bytes()))
        self.assertIn(old_id, row["aliases"])
        self.assertEqual(row["hypothesis_candidates"], [H1])

    def test_hash_mismatch_refuses_alias_join(self):
        self.idea(status="proposed")
        original_path = f"ledger/proposals/{I1}.yaml"
        target_path = "ledger/corrections/schema-supersessions/fixture/bad.v2.yaml"
        target = self.write(target_path, {"idea": {"id": I2, "status": "proposed"}})
        self.write(coverage.REGISTRY_PATH, {"schema": "schema-supersession-registry-v1", "records": [{
            "kind": "ledger", "superseded_path": original_path, "superseded_sha256": "0" * 64,
            "superseding_path": target_path, "superseding_sha256": coverage.sha256(target.read_bytes()),
            "replacement_id": I2,
        }]})
        self.hypothesis(derived_from_idea=I1)
        self.commit()
        report = self.run_inventory()
        row = self.row(report)
        self.assertEqual(row["identity_state"], "unresolved")
        self.assertEqual(row["hypothesis_candidates"], [])
        self.assertIn("supersession_hash_mismatch", {d["code"] for d in report["diagnostics"]})

    def test_identity_change_without_registered_replacement_is_not_joined(self):
        old = self.idea(status="proposed")
        original_path = str(old.relative_to(self.repo))
        target_path = "ledger/corrections/schema-supersessions/fixture/wrong-id.yaml"
        target = self.write(target_path, {"idea": {"id": I2, "status": "proposed"}})
        self.write(coverage.REGISTRY_PATH, {"schema": "schema-supersession-registry-v1", "records": [{
            "kind": "ledger", "superseded_path": original_path,
            "superseded_sha256": coverage.sha256(old.read_bytes()),
            "superseding_path": target_path, "superseding_sha256": coverage.sha256(target.read_bytes()),
        }]})
        self.hypothesis(derived_from_idea=I1)
        self.commit()
        report = self.run_inventory()
        self.assertEqual(self.row(report)["identity_state"], "unresolved")
        self.assertEqual(self.row(report)["hypothesis_candidates"], [])
        self.assertIn("unregistered_identity_change", {d["code"] for d in report["diagnostics"]})

    def test_hypothesis_redirect_joins_legacy_id_to_effective_protocol(self):
        self.idea(status="proposed")
        target = self.hypothesis(derived_from_idea=I1)
        old_path = "ledger/hypotheses/H-XOR-YIELD.yaml"
        old = self.write(old_path, {"hypothesis": {"id": "H-XOR-YIELD"}})
        self.write(coverage.REGISTRY_PATH, {"schema": "schema-supersession-registry-v1", "records": [{
            "kind": "ledger", "superseded_path": old_path,
            "superseded_sha256": coverage.sha256(old.read_bytes()),
            "superseding_path": str(target.relative_to(self.repo)),
            "superseding_sha256": coverage.sha256(target.read_bytes()), "redirect_id": H1,
        }]})
        self.experiment(hypothesis_id="H-XOR-YIELD")
        self.commit()
        report = self.run_inventory()
        self.assertIn(f"experiments/{E1}/specification.yaml", self.row(report)["protocol_path_candidates"])
        self.assertEqual(report["protocols"][0]["hypothesis_bindings"][0]["canonical_id"], H1)

    def test_alternate_queue_schema_is_discovered_focus_and_plan_are_excluded(self):
        self.idea(status="proposed")
        self.experiment(derived_from_idea=I1)
        task = {"id": "TASK-20260907-abc123", "role": "executor", "state": "queued",
                "write_scope": [f"experiments/{E1}/implementation/"]}
        self.queue([task], "execution_queue.json")
        self.queue([task], "focus_queue.json", "crypto.autoresearch.focus_queue.v3")
        self.queue([task], "dispatch_plan.json", "crypto.autoresearch.dispatch_plan.v1")
        self.commit()
        report = self.run_inventory()
        self.assertEqual(len(report["dispatch_queues"]), 1)
        self.assertEqual(len(report["tasks"]), 1)
        self.assertEqual(report["tasks"][0]["owned_experiment_candidates"], [E1])
        self.assertEqual(report["protocols"][0]["owned_task_candidates"][0]["role"], "executor")
        self.assertEqual(report["tasks"][0]["readiness_audit"], "not_performed")

    def test_history_exclusion_and_unowned_task_mentions_do_not_make_source_edges(self):
        self.idea(status="proposed")
        self.idea(I2, status="proposed")
        self.experiment(derived_from_idea=I1,
                        scale_relevance=f"{I2} requires a separate experiment and is out of scope.")
        self.experiment(E2, derived_from_idea=I2)
        self.queue([{"id": "TASK-20260907-abc123", "role": "executor", "state": "completed",
                     "handoff": {"inputs": [f"experiments/{E1}/specification.yaml"]},
                     "write_scope": [f"experiments/{E2}/implementation/driver.py"]}])
        self.commit()
        report = self.run_inventory()
        row = self.row(report, I2)
        self.assertNotIn(f"experiments/{E1}/specification.yaml", row["protocol_path_candidates"])
        self.assertEqual(row["lexical_mentions"][0]["relation"], "lexical_scope_limit_mention")
        task = report["tasks"][0]
        self.assertEqual(task["owned_experiment_candidates"], [E2])
        self.assertEqual(task["lexical_only_experiment_candidates"], [E1])
        protocol = next(p for p in report["protocols"] if p["id"] == E1)
        self.assertEqual(protocol["owned_task_candidates"], [])

    def test_alternate_protocol_versions_and_pointer_documents_are_unresolved(self):
        self.idea(status="proposed")
        self.hypothesis(derived_from_idea=I1)
        self.experiment(filename="specification.json", derived_from_idea=I1)
        self.experiment(filename="specification.v2.yaml", version=2, derived_from_idea=I1)
        target = f"experiments/{E1}/amendments/frozen-contract.yaml"
        self.write(target, {"experiment": {"id": E1, "hypothesis_id": H1, "version": 3}})
        self.queue([{"id": "TASK-20260907-abc123", "handoff": {"inputs": [target]}}])
        self.commit()
        report = self.run_inventory()
        self.assertEqual({p["version"] for p in report["protocols"]}, {1, 2, 3})
        self.assertTrue(all(p["version_authority_audit"] == "not_performed" for p in report["protocols"]))
        self.assertIn(target, self.row(report)["protocol_path_candidates"])

    def test_malformed_alternate_protocol_retained_and_null_coordination_does_not_crash(self):
        self.idea(status="proposed")
        path = f"experiments/{E1}/specification.v2.yaml"
        self.write(path, "experiment: [\n")
        self.write("coordination/fixture/specification.json", "null")
        self.commit()
        report = self.run_inventory()
        protocol = next(p for p in report["protocols"] if p["original_path"] == path)
        self.assertEqual(protocol["identity_state"], "unresolved")
        self.assertEqual(report["dispatch_queues"], [])
        self.assertTrue(report["summary"]["discovery_has_gaps"])

    def test_malformed_ownership_is_not_an_edge_and_counts_as_gap(self):
        self.idea(status="proposed")
        self.hypothesis(derived_from_idea=I1)
        self.experiment()
        self.queue([{"id": "TASK-20260907-abc123", "role": "executor",
                     "write_scope": f"experiments/{E1}/implementation/"}])
        self.commit()
        report = self.run_inventory()
        self.assertEqual(report["tasks"][0]["owned_experiment_candidates"], [])
        self.assertTrue(report["tasks"][0]["ownership_discovery_gaps"])
        self.assertTrue(report["summary"]["discovery_has_gaps"])
        self.assertIn("invalid_task_ownership", {d["code"] for d in report["diagnostics"]})

    def test_generator_identity_is_captured_before_scan(self):
        self.idea(status="proposed")
        self.commit()
        edited_generator = Path(self.tmp.name) / "later-edit.py"
        edited_generator.write_text("# different later bytes\n")
        captured = coverage.GENERATOR_SHA256
        with mock.patch.object(coverage, "__file__", str(edited_generator)):
            report = self.run_inventory()
        self.assertEqual(report["generator"]["sha256"], captured)
        self.assertNotEqual(report["generator"]["sha256"], coverage.sha256(edited_generator.read_bytes()))

    def test_safe_yaml_rejects_python_object_tags(self):
        self.write("ledger/proposals/unsafe.yaml", "!!python/object/apply:os.system ['false']\n")
        self.commit()
        report = self.run_inventory()
        self.assertTrue(any(d["code"] == "parse_error" for d in report["diagnostics"]))
        self.assertEqual(report["ideas"][0]["identity_state"], "unresolved")

    def test_cli_explicit_output_discloses_gaps_and_never_overwrites(self):
        self.idea(question_id="RQ-UNASSIGNED-001")
        self.write("ledger/ideas/broken.yaml", "idea: [\n")
        self.commit()
        output = Path(self.tmp.name) / "report.json"
        args = ["--repo", str(self.repo), "--output", str(output), "--fail-on-gaps"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(coverage.main(args), 1)
        before = output.read_bytes()
        self.assertEqual(json.loads(before)["schema"], coverage.SCHEMA)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(coverage.main(args), 2)
        self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
