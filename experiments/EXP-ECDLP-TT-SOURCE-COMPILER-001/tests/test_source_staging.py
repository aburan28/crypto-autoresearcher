from __future__ import annotations

import hashlib
import os
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
import stage_tt_source_partition as staging
import verify_tt_source_advice as verifier


def file_row(name: str, *, module: bool = False) -> dict[str, object]:
    path = SOURCE_DIR / name
    row: dict[str, object] = {
        "bytes": path.stat().st_size,
        "path": name,
        "sha256": staging.sha256_file(path),
    }
    if module:
        row["module"] = path.stem
    return row


def static_audit_record() -> dict[str, object]:
    record: dict[str, object] = {
        "auditor": {
            "path": "audit_tt_source_closure.py",
            "sha256": staging.sha256_file(SOURCE_DIR / "audit_tt_source_closure.py"),
            "version": 1,
        },
        "cross_role": {
            "performed": True,
            "shared_files": [],
            "shared_inert_package_initializers": [],
            "valid": True,
        },
        "roles": {
            "producer": {
                "closure_files": [
                    file_row(name, module=True)
                    for name in staging.PRODUCER_CLOSURE_FILES
                ],
                "entry": "compile_tt_source_advice.py",
                "role": "producer",
                "valid": True,
                "violations": [],
            },
            "verifier": {
                "closure_files": [
                    file_row(name, module=True)
                    for name in staging.VERIFIER_CLOSURE_FILES
                ],
                "entry": "verify_tt_source_advice.py",
                "role": "verifier",
                "valid": True,
                "violations": [],
            },
        },
        "schema": "exp-ecdlp-tt-source-compiler-capability-audit-v1",
        "valid": True,
        "violations": [],
    }
    record["payload_sha256"] = hashlib.sha256(
        staging.canonical_bytes(record)[:-1]
    ).hexdigest()
    return record


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
    def test_static_audit_is_bound_to_current_source_closures(self) -> None:
        record = static_audit_record()
        staging.validate_static_closure_audit(
            record,
            staging.canonical_bytes(record),
            SOURCE_DIR,
        )

        correct_payload_sha256 = record["payload_sha256"]
        record["payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "payload digest changed"):
            staging.validate_static_closure_audit(
                record,
                staging.canonical_bytes(record),
                SOURCE_DIR,
            )
        record["payload_sha256"] = correct_payload_sha256

        producer = record["roles"]["producer"]  # type: ignore[index]
        producer["closure_files"][0]["sha256"] = "0" * 64  # type: ignore[index]
        record.pop("payload_sha256")
        record["payload_sha256"] = hashlib.sha256(
            staging.canonical_bytes(record)[:-1]
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "producer closure digest changed"):
            staging.validate_static_closure_audit(
                record,
                staging.canonical_bytes(record),
                SOURCE_DIR,
            )

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


if __name__ == "__main__":
    unittest.main()
