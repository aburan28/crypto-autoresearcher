"""Software-only adapter conformance. No solver cohort or service is executed."""
import base64
import hashlib
import gzip
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepare_request
import readiness_probe
import run_experiment as run
import worker
import storage
import fetch_results


def frozen_protocol():
    value = {"schema": "experiment.protocol/v1", "arms": [
        {"id": a, "instrument": {"commit": "a" * 40, "binary_sha256": "b" * 64,
                                  "image_digest": "example.invalid/unit@sha256:" + "c" * 64, "threads": 1}}
        for a in run.ARMS],
        "execution": {"measurement_class": "measurement", "backend": "isolab-k8s",
                      "checkpoint": {"policy": "none"}, "retries": {"max_attempts": 1}}}
    digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    value["freeze"] = {"status": "frozen", "protocol_sha256": digest, "filed_before_affected_data": True}
    return value


class AdapterConformance(unittest.TestCase):
    def setUp(self):
        run.STOP["signal"] = None
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_wait4_preserves_native_failure_without_retry(self):
        out, err = self.root / "stdout", self.root / "stderr"
        rec = run.wait_child([sys.executable, "-c", "import sys; print('one invocation'); sys.exit(3)"], out, err, 5)
        self.assertEqual(rec["exitcode"], 3)
        self.assertEqual(rec["attempts"], 1)
        self.assertIsNone(rec["termination_reason"])
        self.assertFalse(rec["clock"]["wall_valid"])
        self.assertEqual(out.read_text(), "one invocation\n")
        self.assertEqual(rec["rusage"]["maxrss_bytes"], rec["rusage"]["maxrss_raw"] * 1024)

    def test_timeout_is_one_censored_native_invocation(self):
        rec = run.wait_child([sys.executable, "-c", "import time; time.sleep(2)"],
                             self.root / "out", self.root / "err", 0.03)
        self.assertEqual(rec["termination_reason"], "child_timeout")
        self.assertEqual(rec["attempts"], 1)
        self.assertNotEqual(rec["exitcode"], 0)
        self.assertFalse(rec["clock"]["wall_valid"])

    def test_lossless_bounded_line_parts_preserve_original(self):
        raw = self.root / "raw.jsonl"
        original = b'{"unit_test":true,"text":"' + b"x" * 200 + b'"}\n'
        original *= 1000
        raw.write_bytes(original)
        parts = run.split_stream(raw, self.root)
        self.assertTrue(parts["complete"])
        self.assertGreater(len(parts["parts"]), 1)
        self.assertEqual(b"".join((self.root / p["path"]).read_bytes() for p in parts["parts"]), original)
        self.assertTrue(all(p["bytes"] <= 61440 for p in parts["parts"]))
        self.assertEqual(raw.read_bytes(), original)

    def test_oversized_line_retains_original_and_marks_noncomplete_parts(self):
        raw = self.root / "raw.jsonl"
        original = b"x" * 70000 + b"\n"
        raw.write_bytes(original)
        parts = run.split_stream(raw)
        self.assertFalse(parts["complete"])
        self.assertEqual(raw.read_bytes(), original)

    def stream(self, targets):
        base = {"schema": run.ROW_SCHEMA, "scope": "classical_ecdlp_endpoint_reuse",
                "cell_id": "unit-rep0", "fixture": "unit", "replicate": 0, "arm": "harvest"}
        rows = [dict(base, row_kind="fixture_validation"), dict(base, row_kind="setup", known_count=1),
                dict(base, row_kind="initial_endpoint", index=0)]
        rows += [dict(base, row_kind="target", target_id=t["target_id"], target_ordinal=int(t["target_ordinal"]), status="failed") for t in targets]
        raw = self.root / "unit.jsonl"
        raw.write_text("".join(json.dumps(r) + "\n" for r in rows))
        return raw

    def test_complete_failure_rows_are_observations_not_fake_success(self):
        targets = [{"target_id": "unit-t0", "target_ordinal": "0"}, {"target_id": "unit-t1", "target_ordinal": "1"}]
        raw = self.stream(targets)
        result = run.shape_check(raw, "unit-rep0", {"fixture_id": "unit", "replicate": "0"}, "harvest", targets)
        self.assertTrue(result["output_shape_complete"])
        self.assertFalse(result["independent_equation_verification"])

    def test_duplicate_target_record_is_rejected(self):
        targets = [{"target_id": "unit-t0", "target_ordinal": "0"}]
        raw = self.stream(targets)
        with raw.open("a") as stream:
            stream.write(raw.read_text().splitlines()[-1] + "\n")
        with self.assertRaises(ValueError):
            run.shape_check(raw, "unit-rep0", {"fixture_id": "unit", "replicate": "0"}, "harvest", targets)

    def test_protocol_tamper_and_draft_are_refused(self):
        protocol = frozen_protocol()
        path = self.root / "protocol.json"
        path.write_text(json.dumps(protocol))
        run.protocol_read(path)
        protocol["arms"][0]["instrument"]["threads"] = 8
        path.write_text(json.dumps(protocol))
        with self.assertRaises(ValueError):
            run.protocol_read(path)
        protocol = frozen_protocol()
        protocol["freeze"]["status"] = "draft"
        path.write_text(json.dumps(protocol))
        with self.assertRaises(ValueError):
            run.protocol_read(path)

    def archive(self, members):
        file = self.root / "inputs.tar.gz"
        with tarfile.open(file, "w:gz") as tar:
            for name, kind, content in members:
                info = tarfile.TarInfo(name)
                if kind == "symlink":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "/tmp/outside"
                    tar.addfile(info)
                else:
                    info.size = len(content)
                    tar.addfile(info, io.BytesIO(content))
        return file

    def test_safe_input_archive_extracts_regular_public_files_only(self):
        archive = self.archive([("public/inputs-manifest.json", "file", b"{}\n")])
        root = worker.safe_unpack(archive, self.root / "unpack")
        self.assertEqual((root / "inputs-manifest.json").read_bytes(), b"{}\n")

    def test_archive_path_escape_is_refused_before_writing(self):
        archive = self.archive([("public/inputs-manifest.json", "file", b"{}"), ("public/../../outside", "file", b"bad")])
        out = self.root / "unpack"
        with self.assertRaises(ValueError):
            worker.safe_unpack(archive, out)
        self.assertFalse(out.exists())

    def test_archive_symlink_is_refused(self):
        archive = self.archive([("public/inputs-manifest.json", "file", b"{}"), ("public/link", "symlink", b"")])
        with self.assertRaises(ValueError):
            worker.safe_unpack(archive, self.root / "unpack")

    def test_offline_request_maps_exact_upstream_fields_and_never_ready(self):
        protocol = frozen_protocol()
        p = self.root / "protocol.json"
        p.write_text(json.dumps(protocol))
        b = self.root / "build-info.json"
        b.write_text(json.dumps({"schema": "classical.ecdlp.endpoint-reuse.image-build/v1", "source_revision": "a" * 40, "binary_sha256": "b" * 64}))
        req, note = prepare_request.prepare("example.invalid/unit@sha256:" + "c" * 64, "a" * 40, b, p,
                                            "s3://unit-test/inputs/public.tar.gz", "synthetic-unit-version",
                                            "d" * 64, "e" * 64, "unit-only")
        self.assertEqual(set(req), {"job_name", "command", "image", "cpu", "memory", "seconds", "retries"})
        self.assertNotIn("instance_type", req)
        self.assertNotIn("isolation_profile", req)
        self.assertFalse(note["ready"])
        self.assertFalse(note["dispatched"])
        self.assertEqual(req["retries"], 0)
        self.assertEqual(req["command"][:3], ["python3", "/opt/study/execution/worker.py", "--payload-base64"])
        payload = json.loads(base64.b64decode(req["command"][3]))
        self.assertEqual(payload["public_bundle_s3_version_id"], "synthetic-unit-version")
        self.assertEqual(payload["protocol_bytes_sha256"], hashlib.sha256(p.read_bytes()).hexdigest())

    def test_missing_connection_and_digest_fail_before_network(self):
        result = readiness_probe.probe(None, str(self.root / "missing-official-mcp"))
        self.assertFalse(result["ready"])
        self.assertEqual(result["checks"], {})
        self.assertEqual(result["mutations"], [])

    def test_large_artifact_transport_is_lossless_and_records_both_hashes(self):
        path = self.root / "large.jsonl"
        original = b"a" * 1048576
        path.write_bytes(original)
        with storage.stored_payload(path) as (stream, meta):
            encoded = stream.read()
        self.assertEqual(gzip.decompress(encoded), original)
        self.assertEqual(meta["content_encoding"], "gzip")
        self.assertEqual(meta["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(meta["stored_sha256"], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(path.read_bytes(), original)

    def test_committed_image_context_excludes_confirmation_and_private_data(self):
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        package = repo / "study"
        files = ["implementation/build.py", "execution/run_experiment.py", "execution/worker.py",
                 "execution/image_build.py", "execution/Dockerfile", "cohort/public_inputs.py", "protocol/seed_rules.py",
                 "cohort/public/inputs-manifest.json", "cohort/private/synthetic-unit-only.txt", "execution/development/unit.log"]
        for name in files:
            f = package / name
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("synthetic software-conformance data only\n")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.name=unit", "-c", "user.email=unit@example.invalid", "commit", "-qm", "software-only source fixture"], cwd=repo, check=True)
        source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        context = self.root / "context"
        subprocess.run([sys.executable, str(HERE / "prepare_context.py"), "--repo", str(repo),
                        "--package-path", "study", "--source-revision", source, "--output", str(context)],
                       check=True, capture_output=True)
        self.assertTrue((context / "payload/execution/worker.py").is_file())
        self.assertFalse((context / "payload/cohort/public").exists())
        self.assertFalse((context / "payload/cohort/private").exists())
        self.assertFalse((context / "payload/execution/development").exists())

    def test_result_collector_rejects_untrusted_paths(self):
        for value in ("../outside", "/absolute", "a/../../outside", "a//b"):
            with self.assertRaises(ValueError):
                fetch_results.destination(self.root, value)
        self.assertEqual(fetch_results.destination(self.root, "cells/unit/raw.jsonl"), self.root / "cells/unit/raw.jsonl")

    def test_uploader_refuses_nonassigned_prefix_before_sdk_import(self):
        out = self.root / "outputs"
        out.mkdir()
        with patch.dict("os.environ", {"ISOLAB_RESULTS_URI": "s3://unit-test/not-a-job-prefix/"}):
            result = storage.upload_tree(out)
        self.assertFalse(result["payload_upload_complete"])
        self.assertFalse(result["receipt_put_returned"])
        self.assertEqual(result["objects"], [])
        self.assertEqual(result["error_type"], "ValueError")

    def test_schedule_covers_each_cell_once_with_all_six_arms_contiguous(self):
        settings = {f"unit-{i:02d}-rep{r}": {"fixture_id": f"unit-{i:02d}", "replicate": str(r)}
                    for i in range(64) for r in range(2)}
        cohort = SimpleNamespace(settings=settings, protocol_sha256="a" * 64, nonce_hex="b" * 64)
        schedule = run.build_schedule(cohort)
        self.assertEqual(len(schedule), 768)
        self.assertEqual(len(set(schedule)), 768)
        self.assertEqual({c for c, a in schedule}, set(settings))
        for offset in range(0, 768, 6):
            block = schedule[offset:offset + 6]
            self.assertEqual(len({c for c, a in block}), 1)
            self.assertEqual({a for c, a in block}, set(run.ARMS))
        self.assertEqual(schedule, run.build_schedule(cohort))

    def test_final_raw_manifest_binds_protocol_inputs_and_actual_file_bytes(self):
        (self.root / "raw.txt").write_bytes(b"unit-only producer bytes\n")
        flow = {"protocol_sha256": "a" * 64, "inputs_manifest_sha256": "b" * 64}
        info = {"source_revision": "c" * 40, "binary_sha256": "d" * 64}
        manifest = worker.seal_manifest(self.root, flow, info, "a" * 64, "b" * 64)
        self.assertEqual(manifest["protocol_sha256"], "a" * 64)
        self.assertEqual(manifest["inputs_manifest_sha256"], "b" * 64)
        self.assertEqual(manifest["files"][0]["sha256"], hashlib.sha256((self.root / "raw.txt").read_bytes()).hexdigest())
        with self.assertRaises(ValueError):
            worker.seal_manifest(self.root, flow, info, "e" * 64, "b" * 64)


if __name__ == "__main__":
    unittest.main()
