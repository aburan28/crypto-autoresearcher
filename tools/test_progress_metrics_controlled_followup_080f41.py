"""Behavioral committed-source tests; tiny synthetic records, no scientific run."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("successor_metrics", Path(__file__).with_name("progress_metrics.py"))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)
OBS = "docs/reports/classical-ecdlp-controlled-followup-20261029/observations-080f41/observations.json"
RUN = "experiments/EXP-ECDLP-080f41/runs/RUN-ECDLP-939237/"
POST = "experiments/EXP-ECDLP-080f41/postrun-from-view-346631/"
REV = "coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/reviews/"
NATIVE = "experiments/EXP-ECDLP-080f41/reports/run-20261029T2258Z/observations.json"
PROTOCOL = "experiments/EXP-ECDLP-080f41/protocol.json"
SOURCE_POINTER = POST + "export.json.blob.json"
ROOT_POINTER = "experiments/EXP-ECDLP-080f41/export.json.blob.json"


def dump(x):
    return json.dumps(x, sort_keys=True) + "\n"


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


class SuccessorMetricsTests(unittest.TestCase):
    def fixture(self):
        # Counts deliberately differ from the actual study. Planned99999 is
        # irrelevant; one receipt/VM and two logical rows remain distinct.
        controller = {"status": "complete", "vm_creates": 1, "engine_execs": 1,
                      "engine_returncode": 0, "collection_complete": True,
                      "sandbox_id": "synthetic-one-vm", "uid1000_quiescent": True,
                      "termination_ack": {"acknowledged": True}}
        raw = {"run_id": "RUN-ECDLP-939237", "experiment_id": "EXP-ECDLP-080f41",
               "controller": controller}
        counted = {"retained_attempts": 6, "retained_predicate_queries": 24,
                   "strict_recovered_events": 2, "unique_targets_recovered": 1,
                   "unique_targets_retained": 4}
        rows = [{"run_id": "RUN-ECDLP-939237." + method, "arm": "confirmation_" + method,
                 "instance_id": "candidate-vm", "replicate": 0, "status": "succeeded",
                 "measurements": {"counted": counted}} for method in ["original", "incremental"]]
        observed = {"cells": 12, "traces": 6, "intents": 6, "singles": 8, "setups": 2}
        native = {"run_id": "RUN-ECDLP-939237", "experiment_id": "EXP-ECDLP-080f41",
                  "controller": controller, "host_postrun_status": "complete", "host_postrun_errors": [],
                  "logical_evaluator_rows": rows,
                  "coverage": {"retained_curves": 4, "retained_decoder_cells": 12,
                               "retained_physical_trace_records": 6},
                  "recorded_summaries": {"six_cell_totals": [{"cell": "t1.e2", "candidate_events": 3,
                       "candidate_curve_target_pairs": 2, "uniform_events": 0}],
                       "calibration_summary": {"arm_records": 2, "undefined_draws": 0}}}
        documents = {
            RUN + "raw-result.json": dump(raw),
            POST + "verification.json": dump({"status": "checked", "observed": observed,
                 "wall_valid": False, "counter_replay_qualified": False}),
            POST + "postrun-result.json": dump({"status": "complete", "errors": [], "export_findings": [],
                 "scientific_validity": "not_assessed", "wall_valid": False, "counter_replay_qualified": False}),
            POST + "export.validation.json": dump({"findings": [], "protocol_qualified": True, "schema_compliant": True}),
            PROTOCOL: dump({"protocol_id": "EXP-ECDLP-080f41", "sample_size": {"instances": 99999},
                            "freeze": {"status": "frozen", "protocol_sha256": "3" * 64}}),
            NATIVE: dump(native),
            REV + "TASK-20261029-830629/checks.json": dump({"raw": {"counts": observed, "paired": 6,
                 "methods": {"original": counted, "incremental": counted},
                 "cell_summary": {"t1.e2": {"successes": 3}}}}),
        }
        documents[RUN + "execution-receipt.json"] = dump({"schema": "crypto.autoresearch.trial_receipt.v1",
             "run_id": "RUN-ECDLP-939237", "status": "invalid_output", "returncode": 0,
             "check_returncode": 1, "published": False,
             "artifact_sha256": {"raw-result.json": digest(documents[RUN + "raw-result.json"])}})
        views = {}
        for name, pointer_path, review_task, payload_hash in [
                ("source", SOURCE_POINTER, "TASK-20261029-830629", "1" * 64),
                ("root_derivative", ROOT_POINTER, "TASK-20261029-fe803f", "2" * 64)]:
            views[name] = {"payload_sha256": payload_hash, "payload_bytes": 1024}
            documents[pointer_path] = dump({"schema": "crypto.autoresearch.blob_pointer.v1",
                 "encoding": "identity", "sha256": payload_hash, "content_sha256": payload_hash,
                 "size": 1024, "content_size": 1024, "uri": "s3://setec-astronomy-artifacts/store/sha256/" + payload_hash[:2] + "/" + payload_hash})
            documents[REV + review_task + "/experiment.review.json"] = dump({"schema": "experiment.review/v1",
                 "export": {"sha256": payload_hash}, "protocol_sha256": "3" * 64})
        values = {"native_attempts": 1, "native_invalid_output_trials": 1, "native_completed_trials": 0,
                  "vm_creates_recorded": 1, "candidate_engine_execs_recorded": 1, "logical_evaluator_rows": 2,
                  "retained_curves": 4, "retained_decoder_cells": 12, "retained_physical_traces": 6,
                  "retained_single_records": 8, "retained_setups": 2, "paired_confirmation_attempts": 6,
                  "original_strict_recovery_events": 2, "incremental_strict_recovery_events": 2,
                  "primary_t1e2_recovery_events": 3, "primary_t1e2_recovered_targets": 2,
                  "primary_t1e2_recorded_uniform_events": 0, "calibration_arm_records": 2,
                  "calibration_undefined_draws": 0}
        data = {"schema": "classical.ecdlp.controlled-followup.reviewed-observations/v1",
                "experiment_id": "EXP-ECDLP-080f41", "run_id": "RUN-ECDLP-939237",
                "recorded_at": "2026-10-30T00:00:00Z", "native_status": "invalid_output",
                "postrun_status": "complete", "scientific_validity": "not_assessed", "wall_valid": False,
                "counter_replay_qualified": False, "protocol_semantic_sha256": "3" * 64,
                "export_views": views, "metric_source_sha256": {p: digest(t) for p, t in documents.items()},
                "measured_counts": values}
        documents[OBS] = dump(data)
        return documents, data

    def capture(self, documents=None, ref="a" * 40, since="2026-10-29"):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            if documents is None:
                pm.controlled_followup_080f41_observations(ref, since)
            else:
                with mock.patch.object(pm, "show", side_effect=lambda seen_ref, p: documents.get(p)) as show:
                    pm.controlled_followup_080f41_observations(ref, since)
                    self.assertTrue(all(c.args[0] == ref for c in show.call_args_list))
                    # Logical export payloads are deliberately absent. No GET,
                    # working-tree fallback or fake git-show payload is allowed.
                    self.assertFalse(any(c.args[1] in [POST + "export.json", "experiments/EXP-ECDLP-080f41/export.json"]
                                         for c in show.call_args_list))
        return [json.loads(line) for line in stream.getvalue().splitlines()]

    def replace_source(self, documents, data, path, value):
        documents[path] = dump(value)
        data["metric_source_sha256"][path] = digest(documents[path])
        documents[OBS] = dump(data)

    def test_retains_zero_failure_and_one_vm_two_rows_without_plan_counts(self):
        docs, data = self.fixture()
        rows = self.capture(docs)
        self.assertEqual({r["metric"]: r["value"] for r in rows},
                         {"controlled.939237." + k: v for k, v in data["measured_counts"].items()})
        self.assertTrue(all(r["better"] == "neutral" and r["unit"] == "count" for r in rows))
        self.assertEqual(data["measured_counts"]["logical_evaluator_rows"], 2)
        self.assertEqual(data["measured_counts"]["vm_creates_recorded"], 1)
        self.assertEqual(sum(r["value"] == 0 for r in rows), 3)
        self.assertFalse(any(r["value"] == 99999 or r["metric"].startswith("controlled.c8d9b0.") for r in rows))
        self.assertEqual(self.capture(docs, since="2026-10-31"), [])

    def test_missing_stale_hash_malformed_and_substituted_count_sources_emit_nothing(self):
        docs, data = self.fixture()
        for path in data["metric_source_sha256"]:
            for bad in [None, docs[path] + " ", "{broken"]:
                altered = dict(docs)
                if bad is None:
                    del altered[path]
                else:
                    altered[path] = bad
                with self.subTest(path=path, bad=bad):
                    self.assertEqual(self.capture(altered), [])
        for key in data["measured_counts"]:
            for value in [None, True, -1, data["measured_counts"][key] + 1]:
                altered = copy.deepcopy(data);altered["measured_counts"][key] = value
                with self.subTest(count=key, value=value):
                    self.assertEqual(self.capture({**docs, OBS: dump(altered)}), [])

    def test_self_consistent_hash_updates_do_not_qualify_wrong_status_pointer_or_population(self):
        changes = [(RUN + "execution-receipt.json", "status", "output_validated"),
                   (RUN + "execution-receipt.json", "published", True),
                   (POST + "postrun-result.json", "status", "partial"),
                   (POST + "postrun-result.json", "wall_valid", True),
                   (SOURCE_POINTER, "encoding", "gzip"),
                   (SOURCE_POINTER, "uri", "s3://wrong-bucket/store/sha256/11/" + "1" * 64),
                   (SOURCE_POINTER, "content_sha256", "4" * 64),
                   (ROOT_POINTER, "content_size", 7),
                   (REV + "TASK-20261029-fe803f/experiment.review.json", "protocol_sha256", "4" * 64)]
        for path, key, value in changes:
            docs, data = self.fixture();source=json.loads(docs[path]);source[key]=value
            self.replace_source(docs, data, path, source)
            with self.subTest(path=path, key=key):self.assertEqual(self.capture(docs), [])
        for freeze in [{"status": "not_frozen", "protocol_sha256": "3" * 64},
                       {"status": "frozen", "protocol_sha256": "4" * 64}]:
            docs, data = self.fixture();source=json.loads(docs[PROTOCOL]);source["freeze"]=freeze
            self.replace_source(docs,data,PROTOCOL,source)
            with self.subTest(protocol_freeze=freeze):self.assertEqual(self.capture(docs), [])
        for mutate in [lambda n: n["logical_evaluator_rows"][1].update(instance_id="second-vm"),
                       lambda n: n["logical_evaluator_rows"][1].update(run_id="RUN-ECDLP-939237.original")]:
            docs, data = self.fixture();native=json.loads(docs[NATIVE]);mutate(native)
            self.replace_source(docs,data,NATIVE,native);self.assertEqual(self.capture(docs), [])

    def test_real_git_ref_ignores_dirty_sources_and_refuses_later_missing_pointer(self):
        docs, data = self.fixture()
        with tempfile.TemporaryDirectory(prefix="successor-metrics-synthetic-git-") as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
            git("init", "-q");git("config", "user.name", "Synthetic fixture");git("config", "user.email", "fixture@example.invalid")
            for path, text in docs.items():
                dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
            git("add", ".");git("commit", "-qm", "Synthetic committed source fixtures")
            first=git("rev-parse", "HEAD")
            with mock.patch.object(pm, "REPO", root):
                rows=self.capture(ref=first)
                self.assertEqual(len(rows), 19)
                (root/NATIVE).write_text('{"dirty": true}\n')
                self.assertEqual(self.capture(ref=first), rows)
                git("rm", ROOT_POINTER);git("commit", "-qm", "Synthetic missing pointer")
                self.assertEqual(self.capture(ref=git("rev-parse", "HEAD")), [])
                self.assertEqual(self.capture(ref=first), rows)


if __name__ == "__main__":
    unittest.main()
