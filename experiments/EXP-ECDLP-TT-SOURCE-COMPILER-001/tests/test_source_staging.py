from __future__ import annotations

import copy
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = EXPERIMENT_DIR / "src"
sys.path.insert(0, str(SOURCE_DIR))

import attest_tt_backend as backend
import run_tt_source_partition as runner
import run_tt_source_verifier_partition as verifier_runner
import stage_tt_source_partition as staging
import verify_tt_source_advice as verifier


def static_audit_record() -> dict[str, object]:
    return staging.regenerate_static_closure_audit(EXPERIMENT_DIR, SOURCE_DIR)


def validate_static_audit(record: dict[str, object]) -> None:
    staging.validate_static_closure_audit(
        record,
        staging.canonical_bytes(record),
        SOURCE_DIR,
        EXPERIMENT_DIR,
        staging.retain_policy_payloads(EXPERIMENT_DIR),
    )


def populate_stage(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, name in enumerate(runner.EXPECTED_STAGE_FILES, start=1):
        path = root / name
        path.write_bytes(bytes([index]) * index)
        rows.append(
            {
                "path": name,
                "sha256": runner.sha256_file(str(path)),
            }
        )
    return rows


def runtime_with_expected_environment_events(root: Path) -> runner.RuntimeAudit:
    audit = runner.RuntimeAudit(str(root))
    for row in runner.EXPECTED_ENVIRONMENT_EVENTS:
        arguments = (
            (row["key"], row["value"])
            if row["event"] == "os.putenv"
            else (row["key"],)
        )
        audit.audit_hook(row["event"], arguments)
    return audit


class SourceStagingTests(unittest.TestCase):
    def test_source_role_stage_allowlists_are_exact_and_disjoint(self) -> None:
        producer = set(staging.expected_stage_names("producer"))
        verifier_stage = set(staging.expected_stage_names("verifier"))
        self.assertEqual(
            producer - verifier_stage,
            {
                "attest_tt_backend.py",
                "compile_tt_source_advice.py",
                "tt_source_runtime.py",
            },
        )
        self.assertEqual(
            verifier_stage - producer,
            {
                "run_tt_source_verifier_partition.py",
                "source-generator-raw-result.json",
                "verify_tt_source_advice.py",
            },
        )

    def test_source_verifier_receipt_framing_rejects_auxiliary_stderr(self) -> None:
        receipt = {"role": "verifier", "valid": True}
        framed = verifier_runner.RECEIPT_PREFIX + staging.canonical_bytes(receipt)
        observed, auxiliary = staging.parse_source_verifier_receipt(framed)
        self.assertEqual(observed, receipt)
        self.assertEqual(auxiliary, b"")
        for invalid in (b"warning\n" + framed, framed + b"\n", framed + b" \n"):
            with self.subTest(invalid=invalid[-16:]):
                with self.assertRaises(ValueError):
                    staging.parse_source_verifier_receipt(invalid)
        with self.assertRaisesRegex(ValueError, "byte gate"):
            staging.parse_source_verifier_receipt(
                verifier_runner.RECEIPT_PREFIX
                + b"x" * staging.MAX_VERIFIER_STDERR_BYTES
            )

    def test_source_verifier_bootstrap_separates_parent_arguments(self) -> None:
        verifier_args, stage_digest, audit_digest = verifier_runner.parse_bootstrap_args(
            [
                "--manifest",
                "source-instance-manifest-v1.json",
                "--execution-matrix",
                "source-execution-matrix-v2.json",
                "--raw-result",
                "source-generator-raw-result.json",
                "--expected-static-closure-audit-sha256",
                "1" * 64,
                "--strict-preflight-development",
                "--expected-stage-sha256",
                "2" * 64,
                "--static-audit-sha256",
                "3" * 64,
            ]
        )
        self.assertIn("--strict-preflight-development", verifier_args)
        self.assertNotIn("--expected-stage-sha256", verifier_args)
        self.assertEqual(stage_digest, "2" * 64)
        self.assertEqual(audit_digest, "3" * 64)

    def test_static_audit_is_bound_to_current_source_closures(self) -> None:
        record = static_audit_record()
        validate_static_audit(record)

        correct_payload_sha256 = record["payload_sha256"]
        record["payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "payload digest changed"):
            validate_static_audit(record)
        record["payload_sha256"] = correct_payload_sha256

        producer = record["roles"]["producer"]  # type: ignore[index]
        producer["closure_files"][0]["sha256"] = "0" * 64  # type: ignore[index]
        record.pop("payload_sha256")
        record["payload_sha256"] = hashlib.sha256(
            staging.canonical_bytes(record)[:-1]
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "producer closure digest changed"):
            validate_static_audit(record)

    def test_static_audit_binds_source_supervisor_closure(self) -> None:
        record = static_audit_record()
        harness = record["harness"]  # type: ignore[index]
        self.assertEqual(
            {row["path"] for row in harness["files"]},  # type: ignore[index]
            set(staging.EXPECTED_HARNESS_FILES),
        )
        harness["files"][0]["sha256"] = "0" * 64  # type: ignore[index]
        record.pop("payload_sha256")
        record["payload_sha256"] = hashlib.sha256(
            staging.canonical_bytes(record)[:-1]
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "static source harness changed"):
            validate_static_audit(record)

    def test_static_audit_binds_policy_hashes_and_parent_replay(self) -> None:
        altered_policy = static_audit_record()
        policy = altered_policy["policy"]  # type: ignore[index]
        policy["environment_allowlist"].append("FORGED_ENVIRONMENT")  # type: ignore[index]
        altered_policy.pop("payload_sha256")
        altered_policy["payload_sha256"] = hashlib.sha256(
            staging.canonical_bytes(altered_policy)[:-1]
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "fresh parent replay"):
            validate_static_audit(altered_policy)

        altered_hash = static_audit_record()
        policy = altered_hash["policy"]  # type: ignore[index]
        policy["policy_file_hashes"][0]["sha256"] = "0" * 64  # type: ignore[index]
        altered_hash.pop("payload_sha256")
        altered_hash["payload_sha256"] = hashlib.sha256(
            staging.canonical_bytes(altered_hash)[:-1]
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "policy hashes changed"):
            validate_static_audit(altered_hash)

    def test_atomic_publication_breaks_preexisting_hardlink_alias(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-source-hardlink-publication-",
                dir="/private/tmp",
            )
        )
        try:
            output = root / "source-output.json"
            receipt_path = root / "source-receipt.json"
            output.write_bytes(b"old")
            os.link(output, receipt_path)
            self.assertEqual(output.stat().st_ino, receipt_path.stat().st_ino)

            output_payload = staging.canonical_bytes({"artifact": "source"})
            receipt: dict[str, object] = {"schema": "test-receipt", "valid": True}
            staging.publish_output_and_receipt(
                output,
                output_payload,
                receipt_path,
                receipt,
            )
            self.assertEqual(output.read_bytes(), output_payload)
            self.assertEqual(
                receipt_path.read_bytes(),
                staging.canonical_bytes(receipt),
            )
            self.assertNotEqual(output.stat().st_ino, receipt_path.stat().st_ino)
        finally:
            shutil.rmtree(root)

    def test_appledouble_cleanup_is_scoped_and_other_extra_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (*staging.SOURCE_FILES, *staging.DATA_FILES):
                (root / name).write_bytes(b"x")
            (root / "._compile_tt_source_advice.py").write_bytes(b"metadata")

            staging.remove_appledouble_files(root)
            staging.validate_staged_file_set(root)
            (root / "unexpected.json").write_bytes(b"{}")
            with self.assertRaisesRegex(RuntimeError, "staged file set differs"):
                staging.validate_staged_file_set(root)

    def test_runtime_audit_rejects_unapproved_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            populate_stage(root)
            cases = (
                ("write", "open", (str(root / runner.EXPECTED_STAGE_FILES[0]), "w", 0)),
                ("child", "subprocess.Popen", ()),
                ("process_replace", "os.exec", ()),
                ("network", "socket.connect", ()),
                ("environment", "os.putenv", ()),
            )
            for label, event, arguments in cases:
                with self.subTest(label=label):
                    audit = runner.RuntimeAudit(str(root))
                    with self.assertRaises(PermissionError):
                        audit.audit_hook(event, arguments)
                    self.assertEqual(len(audit.denied_events), 1)

            audit = runner.RuntimeAudit(str(root))
            with self.assertRaises(PermissionError):
                audit.check_path("open", root / "target-instance-manifest-v1.json")
            cache_probe = next(
                path for path in audit.cache_probe_paths if path.endswith(".pyc")
            )
            clean_audit = runner.RuntimeAudit(str(root))
            clean_audit.check_path("open", cache_probe)
            self.assertEqual(clean_audit.denied_events, [])

    def test_runtime_receipt_binds_environment_and_stage_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = populate_stage(root)
            expected_digest = runner.stage_digest(rows)
            with mock.patch.dict(os.environ, runner.EXPECTED_ENVIRONMENT, clear=True):
                receipt = runtime_with_expected_environment_events(root).receipt(
                    static_audit_sha256="1" * 64,
                    expected_stage_sha256=expected_digest,
                    started_ns=1,
                )
                self.assertTrue(receipt["valid"])

                changed_stage = runtime_with_expected_environment_events(root).receipt(
                    static_audit_sha256="1" * 64,
                    expected_stage_sha256="0" * 64,
                    started_ns=1,
                )
                self.assertFalse(changed_stage["valid"])

            drifted_environment = dict(runner.EXPECTED_ENVIRONMENT)
            drifted_environment["EXTRA"] = "1"
            with mock.patch.dict(os.environ, drifted_environment, clear=True):
                drifted = runtime_with_expected_environment_events(root).receipt(
                    static_audit_sha256="1" * 64,
                    expected_stage_sha256=expected_digest,
                    started_ns=1,
                )
                self.assertFalse(drifted["valid"])

    def test_runtime_receipt_digest_mutation_is_rejected(self) -> None:
        receipt = {"schema": "test", "valid": True}
        digest = hashlib.sha256(verifier.canonical_bytes(receipt)).hexdigest()
        provenance = {"runtime_receipt_sha256": digest}
        self.assertEqual(
            verifier.audit_runtime_receipt_digest(receipt, provenance),
            digest,
        )
        mutated = {"schema": "test", "valid": False}
        with self.assertRaises(verifier.VerificationError) as context:
            verifier.audit_runtime_receipt_digest(mutated, provenance)
        self.assertEqual(context.exception.code, "runtime_receipt_digest_mismatch")

    def test_artifact_freeze_mode_is_unavailable_without_execution_plan(self) -> None:
        arguments = [
            "--manifest",
            str(EXPERIMENT_DIR / "source-instance-manifest-v1.json"),
            "--execution-matrix",
            str(EXPERIMENT_DIR / "source-execution-matrix-v2.json"),
            "--raw-result",
            "source-generator-raw-result.json",
        ]
        with self.assertRaises(verifier.VerificationError) as context:
            verifier.parse_args(arguments)
        self.assertEqual(context.exception.code, "execution_not_authorized")

        with self.assertRaises(verifier.VerificationError) as context:
            verifier.parse_args([*arguments, "--strict-preflight-development"])
        self.assertEqual(context.exception.code, "argument_error")

        parsed = verifier.parse_args(
            [
                *arguments,
                "--strict-preflight-development",
                "--expected-static-closure-audit-sha256",
                "1" * 64,
            ]
        )
        self.assertEqual(parsed.expected_static_closure_audit_sha256, "1" * 64)

    def test_backend_platform_identity_does_not_use_platform_shell_probe(self) -> None:
        with mock.patch.object(
            backend.platform,
            "platform",
            side_effect=AssertionError("shell-backed platform probe used"),
        ):
            self.assertEqual(
                backend.normalized_platform(),
                "macOS-15.6-arm64-arm-64bit-Mach-O",
            )

    def test_parent_binds_source_backend_values_to_matrix(self) -> None:
        backend_gate = {
            "array_order": "C",
            "dtype": "int64",
            "machine": "arm64",
            "numpy_distribution_file_count": 1,
            "numpy_installed_closure_sha256": "unused",
            "numpy_multiarray_umath_sha256": "2" * 64,
            "numpy_version": "2.4.0",
            "os_loader_dependencies": ["/expected/loader"],
            "platform": "test-platform",
            "python_executable": "/test/python",
            "python_executable_sha256": "3" * 64,
            "python_version": "test-python",
            "thread_count": 1,
        }
        member = {"bytes": 1, "path": "numpy/test.py", "sha256": "1" * 64}
        digest = hashlib.sha256()
        digest.update(member["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(member["sha256"]))
        closure = digest.hexdigest()
        backend_gate["numpy_installed_closure_sha256"] = closure
        expectations = staging.source_backend_expectations(backend_gate)
        record = {
            "boundary": "test",
            "checks": [
                {
                    "expected": expectations[field],
                    "field": field,
                    "match": True,
                    "observed": expectations[field],
                }
                for field in staging.SOURCE_BACKEND_CHECK_FIELDS
            ],
            "observed": {
                "expected_os_loader_dependencies": ["/expected/loader"],
                "loaded_numpy_extensions": [
                    {"path": "/numpy/_multiarray_umath.so", "sha256": "2" * 64}
                ],
                "loaded_os_images": ["/expected/loader"],
                "numpy_distribution_members": [member],
                "numpy_installed_closure_sha256": closure,
                "numpy_multiarray_umath": {
                    "path": "/numpy/_multiarray_umath.so",
                    "sha256": "2" * 64,
                },
                "python_executable": "/test/python",
                "python_raw_version": "test-python",
                "thread_environment": dict(staging.EXPECTED_ENVIRONMENT),
            },
            "protocol": "EXP-ECDLP-TT-SOURCE-COMPILER-001-BACKEND-ATTESTATION-V1",
            "source_execution_matrix": {
                "path": "source-execution-matrix-v2.json",
                "sha256": "4" * 64,
            },
            "valid": True,
        }
        staging.validate_source_backend_attestation(
            record,
            backend_gate=backend_gate,
            matrix_sha256="4" * 64,
            runtime_boundary={
                "numpy_distribution": {"file_count": 1, "sha256": closure}
            },
        )
        forged = copy.deepcopy(record)
        forged["checks"][0]["expected"] = "forged"
        forged["checks"][0]["observed"] = "forged"
        with self.assertRaisesRegex(ValueError, "backend value changed"):
            staging.validate_source_backend_attestation(
                forged,
                backend_gate=backend_gate,
                matrix_sha256="4" * 64,
                runtime_boundary={
                    "numpy_distribution": {"file_count": 1, "sha256": closure}
                },
            )

    def test_parent_rejects_post_copy_pre_snapshot_mutation(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-source-approved-manifest-",
                dir="/Volumes/Volume/autolab/tmp",
            )
        )
        try:
            approved: list[dict[str, object]] = []
            for name in staging.expected_stage_names():
                approved.append(
                    staging.supervisor.stage_retained_payload(
                        root / name,
                        name.encode("ascii"),
                        staging.MAX_INPUT_BYTES,
                    )
                )
            staging.remove_appledouble_files(root)
            target = root / "run_tt_source_partition.py"
            target.write_bytes(b"X" * target.stat().st_size)
            staging.remove_appledouble_files(root)
            observed = staging.collect_stage_rows(root)
            with self.assertRaisesRegex(RuntimeError, "parent-retained approved bytes"):
                staging.validate_approved_stage_manifest(approved, observed)
        finally:
            shutil.rmtree(root)

    @unittest.skipUnless(sys.platform == "darwin", "kqueue vnode is macOS-specific")
    def test_supervisor_rejects_transient_stage_namespace_race(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-source-race-test-",
                dir="/Volumes/Volume/autolab/tmp",
            )
        )
        try:
            stage = root / "stage"
            stage.mkdir()
            for name in staging.expected_stage_names():
                (stage / name).write_text(name, encoding="ascii")
            staging.remove_appledouble_files(stage)
            transient = stage / "not-in-stage-rows.txt"
            with staging.StageMutationMonitor(stage) as monitor:
                helper = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        "-B",
                        "-c",
                        (
                            "from pathlib import Path; "
                            "p=Path(__import__('sys').argv[1]); "
                            "p.write_text('transient', encoding='ascii'); "
                            "p.read_text(encoding='ascii'); p.unlink()"
                        ),
                        str(transient),
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertEqual(helper.returncode, 0)
                events = monitor.poll()
            self.assertTrue(events)
            with self.assertRaisesRegex(RuntimeError, "source stage mutated"):
                staging.reject_stage_mutations(events)
        finally:
            shutil.rmtree(root)

    @unittest.skipUnless(sys.platform == "darwin", "APFS race control is macOS-specific")
    def test_monitor_setup_rejects_apfs_inode_substitution(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-source-apfs-race-",
                dir="/private/tmp",
            )
        )
        try:
            stage = root / "stage"
            stage.mkdir()
            for name in staging.expected_stage_names():
                (stage / name).write_text(name, encoding="ascii")
            target = stage / staging.expected_stage_names()[0]
            replacement = root / "same-bytes-replacement.txt"
            replacement.write_bytes(target.read_bytes())
            real_open = staging.os.open
            substituted = False

            def racing_open(path: object, flags: int, *args: object) -> int:
                nonlocal substituted
                descriptor = real_open(path, flags, *args)
                if Path(path) == target and not substituted:
                    staging.os.replace(replacement, target)
                    substituted = True
                return descriptor

            with mock.patch.object(staging.os, "open", side_effect=racing_open):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "vnode binding changed|source stage mutated",
                ):
                    staging.StageMutationMonitor(stage)
            self.assertTrue(substituted)
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
