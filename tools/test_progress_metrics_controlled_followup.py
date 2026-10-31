"""Committed-source operational metrics; fixed synthetic Git fixture, no trial."""
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

SPEC = importlib.util.spec_from_file_location("controlled_progress_metrics", Path(__file__).with_name("progress_metrics.py"))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)
OBS = "docs/reports/classical-ecdlp-controlled-followup-20261029/observations/observations.json"
RUN = "experiments/EXP-ECDLP-956f81/runs/RUN-ECDLP-c8d9b0/"
POST = "experiments/EXP-ECDLP-956f81/postrun/"
PROTOCOL = "experiments/EXP-ECDLP-956f81/protocol.json"


def dump(value):
    return json.dumps(value, sort_keys=True) + "\n"


class ControlledFollowupMetricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the committed pinned protocol only to seed a small synthetic repo.
        # The exporter itself will then read every payload from that synthetic Git.
        source = Path(__file__).resolve().parents[1]
        # Outside delivery may run before canonical publication; use the same
        # already committed source repository, never a working-tree protocol.
        if not (source / ".git").exists():
            source = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
        cls.protocol = subprocess.check_output(["git", "-C", str(source), "show", "HEAD:" + PROTOCOL], text=True)
        if hashlib.sha256(cls.protocol.encode()).hexdigest() != "0b6e90a9cf9d79dd40fc43966c8aefd15cd6007feeb8ebf76f5ced3bb3149636":
            raise AssertionError("committed fixture protocol is not the pinned historical source")

    def fixture(self, vm_creates=1, findings=4):
        documents = {
            PROTOCOL: self.protocol,
            RUN + "raw-result.json": dump({
                "experiment_id": "EXP-ECDLP-956f81", "run_id": "RUN-ECDLP-c8d9b0",
                "operational_status": "failed", "scientific_validity": "not_assessed",
                "controller": {"status": "failed", "collection_complete": False,
                               "files": [], "vm_creates": vm_creates, "engine_execs": 0}}),
            POST + "export.canonical-paths.json": dump({"schema": "experiment.export/v1", "runs": [],
                                                       "flow": {"planned": 99999}}),
            POST + "export.validation.json": dump({"schema_compliant": True, "protocol_qualified": False,
                                                   "findings": ["missing-" + str(i) for i in range(findings)]}),
            POST + "postrun-result.json": dump({"status": "incomplete", "wall_valid": False,
                                                 "scientific_validity": "not_assessed", "counter_replay_qualified": False,
                                                 "export_findings": ["missing-" + str(i) for i in range(findings)]}),
        }
        documents[RUN + "execution-receipt.json"] = dump({
            "schema": "crypto.autoresearch.trial_receipt.v1", "run_id": "RUN-ECDLP-c8d9b0",
            "status": "infrastructure_error", "returncode": 1, "check_returncode": None,
            "artifact_sha256": {"raw-result.json": hashlib.sha256(documents[RUN + "raw-result.json"].encode()).hexdigest()}})
        data = {
            "schema": "classical.ecdlp.controlled-followup.failed-observations/v1",
            "experiment_id": "EXP-ECDLP-956f81", "run_id": "RUN-ECDLP-c8d9b0", "recorded_at": "2026-10-29T00:00:00Z",
            "native_status": "infrastructure_error", "postrun_status": "incomplete", "scientific_validity": "not_assessed",
            "wall_valid": False, "counter_replay_qualified": False,
            "metric_source_sha256": {p: hashlib.sha256(t.encode()).hexdigest() for p, t in documents.items()},
            "measured_counts": {"attempted_trials": 1, "completed_trials": 0, "failed_infrastructure_trials": 1,
                                "timed_out_trials": 0, "vm_creates_recorded": vm_creates,
                                "candidate_engine_execs_recorded": 0, "retained_logical_evaluator_rows": 0,
                                "missing_coverage_findings": findings},
            "frozen_plan_metadata_only": {"curves": 999999, "physical_calls_before_controls": 888888},
            "scientific_measurements": {"recovery_rate": None, "predicate_calls": None},
        }
        documents[OBS] = dump(data)
        return documents, data

    def capture(self, ref="a" * 40, since="2026-10-29"):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pm.controlled_followup_observations(ref, since)
        return [json.loads(line) for line in output.getvalue().splitlines()]

    def test_source_hash_status_and_count_gating(self):
        documents, data = self.fixture()
        def show(ref, path):
            self.assertEqual(ref, "a" * 40)
            return documents.get(path)
        with mock.patch.object(pm, "show", side_effect=show):
            rows = self.capture()
        self.assertEqual({r["metric"]: r["value"] for r in rows},
                         {"controlled.c8d9b0." + k: v for k, v in data["measured_counts"].items()})
        self.assertTrue(all(r["better"] == "neutral" and r["kind"] == "gauge" and r["unit"] == "count"
                            and r["source"] == OBS + "@" + "a" * 40 for r in rows))
        self.assertEqual({r["value"] for r in rows}, {0, 1, 4})
        # Failed status is retained; fake success, clocks and scientific claims are refused.
        for key, value in (("native_status", "output_validated"), ("postrun_status", "complete"),
                           ("scientific_validity", "passed"), ("wall_valid", True),
                           ("counter_replay_qualified", True), ("experiment_id", "EXP-ECDLP-000000")):
            bad = copy.deepcopy(data);bad[key] = value
            with self.subTest(key=key), mock.patch.object(pm, "show", side_effect=lambda ref, path: dump(bad) if path == OBS else documents.get(path)):
                self.assertEqual(self.capture(), [])
        for field in data["measured_counts"]:
            for value in (None, True, -1, data["measured_counts"][field] + 1):
                bad = copy.deepcopy(data);bad["measured_counts"][field] = value
                with self.subTest(field=field, value=value), mock.patch.object(pm, "show", side_effect=lambda ref, path: dump(bad) if path == OBS else documents.get(path)):
                    self.assertEqual(self.capture(), [])
        for path in data["metric_source_sha256"]:
            for changed in (None, documents[path] + " "):
                with self.subTest(path=path, changed=changed is None), mock.patch.object(pm, "show", side_effect=lambda ref, p: changed if p == path else documents.get(p)):
                    self.assertEqual(self.capture(), [])
        for field in ("measured_counts", "metric_source_sha256", "recorded_at"):
            bad = copy.deepcopy(data);del bad[field]
            with self.subTest(missing=field), mock.patch.object(pm, "show", side_effect=lambda ref, path: dump(bad) if path == OBS else documents.get(path)):
                self.assertEqual(self.capture(), [])
        with mock.patch.object(pm, "show", side_effect=show):
            self.assertEqual(self.capture(since="2026-10-30"), [])

    def test_counts_are_recomputed_not_hardcoded_or_planned(self):
        # A failure before VM creation and two findings are synthetic mechanics,
        # deliberately different from the actual old run. Plan metadata is ignored.
        documents, data = self.fixture(vm_creates=0, findings=2)
        with mock.patch.object(pm, "show", side_effect=lambda ref, path: documents.get(path)):
            rows = self.capture()
        self.assertEqual({r["metric"]: r["value"] for r in rows},
                         {"controlled.c8d9b0." + k: v for k, v in data["measured_counts"].items()})
        self.assertFalse(any("recover" in r["metric"] or "predicate" in r["metric"] or r["value"] > 2 for r in rows))

    def test_real_git_snapshot_ignores_dirty_files_and_missing_source(self):
        documents, data = self.fixture()
        with tempfile.TemporaryDirectory(prefix="controlled-metrics-fixture-") as tmp:
            repo = Path(tmp)
            def git(*argv):
                return subprocess.check_output(["git", "-C", str(repo), *argv], text=True, stderr=subprocess.DEVNULL).strip()
            git("init", "-q")
            for path, text in documents.items():
                target = repo / path;target.parent.mkdir(parents=True, exist_ok=True);target.write_text(text)
            git("add", ".")
            git("-c", "user.name=Metrics fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixed synthetic source")
            head = git("rev-parse", "HEAD")
            (repo / OBS).write_text("{}")
            (repo / (RUN + "raw-result.json")).write_text("corrupt dirty working tree")
            with mock.patch.object(pm, "REPO", repo):
                rows = self.capture(ref=head)
            self.assertEqual(len(rows), len(data["measured_counts"]))
            self.assertTrue(all(r["source"] == OBS + "@" + head for r in rows))
            # A new committed source deletion invalidates the source-bound series.
            git("rm", "-f", RUN + "raw-result.json")
            git("-c", "user.name=Metrics fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "remove required source")
            with mock.patch.object(pm, "REPO", repo):
                self.assertEqual(self.capture(ref=git("rev-parse", "HEAD")), [])


if __name__ == "__main__":
    unittest.main()
