"""Regression coverage for committed-state progress exports."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("progress_metrics.py")
spec = importlib.util.spec_from_file_location("progress_metrics", SCRIPT)
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)


class ProgressMetricsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Exporter tests")
        self.write("README.md", "fixture\n")
        self.commit()
        self.patch = mock.patch.object(pm, "REPO", self.repo)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args], text=True).strip()

    def write(self, path, data):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def cli(self, *args):
        env = {k: v for k, v in os.environ.items() if not k.startswith("PM_")}
        env["PM_REPO_PATH"] = str(self.repo)
        return subprocess.run([sys.executable, str(SCRIPT), *args], env=env, text=True, capture_output=True)

    def capture(self, function, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            function(*args)
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_invalid_ref_is_an_error_without_zero_samples(self):
        for ref in ("missing-branch", "--all"):
            result = self.cli("--ref=" + ref)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_default_remote_branch_is_used_and_sources_pin_its_commit(self):
        self.write("claims/a.json", "{}")
        old = self.commit()
        self.git("update-ref", "refs/remotes/origin/main", old)
        self.write("claims/b.json", "{}")
        current = self.commit()
        self.git("update-ref", "refs/remotes/origin/current", current)
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/current")
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        row = next(r for r in map(json.loads, result.stdout.splitlines()) if r["metric"] == "claims.records")
        self.assertEqual(row["value"], 2)
        self.assertIn(current, row["source"])

    def test_one_snapshot_survives_a_branch_move_during_export(self):
        self.write("claims/a.json", "{}")
        old = self.commit()
        self.write("claims/b.json", "{}")
        new = self.commit()
        self.git("update-ref", "refs/remotes/origin/main", old)
        def move_branch(ref, since):
            self.git("update-ref", "refs/remotes/origin/main", new)
        with mock.patch.object(sys, "argv", [str(SCRIPT), "--ref", "origin/main"]), mock.patch.object(pm, "census", move_branch):
            rows = self.capture(pm.main)
        row = next(r for r in rows if r["metric"] == "claims.records")
        self.assertEqual(row["value"], 1)
        self.assertIn(old, row["source"])

    def test_nonfinite_boolean_and_overflow_values_are_not_json_samples(self):
        for value in (float("inf"), float("-inf"), float("nan"), True, 10**400):
            self.assertEqual(self.capture(pm.emit, "invalid", value), [])
        self.assertEqual(self.capture(pm.emit, "zero", 0)[0]["value"], 0)

    def test_missing_sources_emit_no_estimated_zero_counts(self):
        result = self.cli("--ref", "HEAD")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def funnel_rows(self, values):
        document = json.dumps({"kpis": {"funnel": values}})
        with mock.patch.object(pm, "file_history", return_value=[("2026-10-22", "a" * 40, document)]):
            return self.capture(pm.funnel, "HEAD", "2026-10-01")

    def test_missing_unrun_count_does_not_claim_full_conversion(self):
        rows = self.funnel_rows({"approved": 4, "experiments_with_runs": 3})
        self.assertNotIn("funnel.approved_to_run_pct", [r["metric"] for r in rows])

    def test_measured_zero_unrun_count_does_report_full_conversion(self):
        rows = self.funnel_rows({"approved": 4, "approved_unrun": 0, "experiments_with_runs": 3})
        self.assertEqual(next(r["value"] for r in rows if r["metric"] == "funnel.approved_to_run_pct"), 100)

    def test_malformed_manifests_do_not_crash_or_count_as_valid(self):
        self.write("experiments/a/runs/one/manifest.json", "[]")
        self.write("experiments/a/runs/two/manifest.json", '{"run": "unknown"}')
        self.write("experiments/a/runs/three/manifest.json", '{"status": "invalid_measurement"}')
        self.write("experiments/a/runs/four/manifest.json", '{"status": "partial_failed_infrastructure"}')
        self.commit()
        rows = self.capture(pm.runs, "HEAD")
        values = {r["metric"]: r["value"] for r in rows}
        self.assertEqual(values["runs.manifests_total"], 4)
        self.assertEqual(values["runs.completed_valid"], 0)
        self.assertEqual(values["runs.failed_or_invalid"], 2)

    def add_icperf_fixture(self):
        for exp_id, runs in pm.ICPERF_RUNS.items():
            schema = f"crypto.autoresearch.{exp_id.lower()}.stage0.v2"
            for run_id, trial_id in runs.items():
                base = f"experiments/{exp_id}/runs/{run_id}"
                raw = {"schema": schema, "experiment_id": exp_id, "run_id": run_id,
                       "trial_id": trial_id, "attack_claimed": False}
                if exp_id == "EXP-ICPERF-283a70":
                    raw.update({"n_targets": 64, "sample_sum": 2943, "median": 28})
                else:
                    raw.update({"states": 10, "c_probe_ns": 370, "c_state_ns": 2100, "c_step_ns": 40})
                raw_text = json.dumps(raw, sort_keys=True)
                manifest_text = "run: fixture\n"
                hashes = {"raw-result.json": hashlib.sha256(raw_text.encode()).hexdigest(),
                          "manifest.yaml": hashlib.sha256(manifest_text.encode()).hexdigest()}
                receipt = {"schema": "crypto.autoresearch.trial_receipt.v1", "run_id": run_id,
                           "trial_id": trial_id, "status": "output_validated", "returncode": 0,
                           "check_returncode": 0, "finished_at": "2026-10-30T15:00:00Z",
                           "artifact_sha256": hashes,
                           "manifest_completion": {"driver_manifest_sha256": hashes["manifest.yaml"]}}
                self.write(f"{base}/raw-result.json", raw_text)
                self.write(f"{base}/manifest.yaml", manifest_text)
                self.write(f"{base}/execution-receipt.json", json.dumps(receipt))
        return self.commit()

    def test_icperf_rows_require_matching_committed_receipts_and_preserve_units(self):
        self.add_icperf_fixture()
        rows = self.capture(pm.icperf_trials, "HEAD", "2026-10-01")
        trial_events = [r for r in rows if r["metric"].endswith("validated_trials")]
        self.assertEqual(len(trial_events), 9)
        metrics = {r["metric"]: r for r in rows}
        sample = metrics["icperf.EXP-ICPERF-283a70.geometric-probe-sample.sample_sum"]
        self.assertEqual((sample["value"], sample["unit"]), (2943, "probe-count sum"))
        modeled = metrics["icperf.EXP-ICPERF-284bc4.price-ratio-identity.c_probe_ns"]
        self.assertEqual((modeled["value"], modeled["unit"]), (370, "nanoseconds per probe"))

    def test_icperf_cohort_is_not_partially_exported_after_receipt_mismatch(self):
        self.add_icperf_fixture()
        self.write("experiments/EXP-ICPERF-283a70/runs/RUN-ICPERF-f21eb1/raw-result.json", "{}")
        self.commit()
        self.assertEqual(self.capture(pm.icperf_trials, "HEAD", "2026-10-01"), [])

    def test_working_tree_changes_and_nested_claim_json_are_excluded(self):
        self.write("claims/a.json", "{}")
        self.write("claims/schema/schema.json", "{}")
        self.commit()
        self.write("claims/uncommitted.json", "{}")
        rows = self.capture(pm.claims, "HEAD")
        self.assertEqual(rows[0]["value"], 1)

    def test_invalid_since_date_is_refused(self):
        result = self.cli("--ref", "HEAD", "--since", "2026-99-99")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
