from __future__ import annotations

import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = EXPERIMENT_DIR / "src"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

import audit_tt_target_closure as closure_audit  # noqa: E402
import run_tt_target_partition as child  # noqa: E402
import stage_tt_target_partition as parent  # noqa: E402


class TargetStagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = closure_audit.audit_closures(
            SOURCE_DIR,
            SOURCE_DIR / "compile_tt_target_advice.py",
            SOURCE_DIR / "verify_tt_target_advice.py",
        )
        cls.audit_bytes = parent.canonical_bytes(cls.audit)

    @staticmethod
    def runtime_boundary(read_filters: list[dict[str, str]]) -> dict[str, object]:
        boundary: dict[str, object] = {
            "read_filters": read_filters,
            "schema": "tt-target-parent-runtime-boundary-development-v1",
        }
        boundary["closure_sha256"] = parent.sha256_bytes(
            parent.canonical_bytes(boundary)
        )
        return boundary

    def test_role_stage_allowlists_are_exact_and_disjoint(self) -> None:
        producer = set(parent.expected_stage_names("producer"))
        verifier = set(parent.expected_stage_names("verifier"))

        self.assertEqual(
            producer - verifier,
            {
                "compile_tt_target_advice.py",
                "tt_target_coefficients.py",
                "tt_target_runtime.py",
            },
        )
        self.assertEqual(
            verifier - producer,
            {"target-raw-result.json", "verify_tt_target_advice.py"},
        )

    def test_static_audit_binds_each_role_source_hash(self) -> None:
        for role in ("producer", "verifier"):
            parent.validate_static_audit(
                self.audit,
                self.audit_bytes,
                role=role,
                source_dir=SOURCE_DIR,
            )

        forged = copy.deepcopy(self.audit)
        forged["producer"]["reports"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "closure changed"):
            parent.validate_static_audit(
                forged,
                parent.canonical_bytes(forged),
                role="producer",
                source_dir=SOURCE_DIR,
            )
        self.assertEqual(
            {row["path"] for row in self.audit["harness"]["files"]},
            set(parent.EXPECTED_HARNESS_FILES),
        )

    def test_child_receipt_framing_rejects_auxiliary_stderr(self) -> None:
        receipt = {"role": "producer", "valid": True}
        framed = parent.RECEIPT_PREFIX + parent.canonical_bytes(receipt)

        observed, auxiliary = parent.parse_child_receipt(framed)
        self.assertEqual(observed, receipt)
        self.assertEqual(auxiliary, b"")

        _, auxiliary = parent.parse_child_receipt(b"warning\n" + framed)
        self.assertEqual(auxiliary, b"warning\n")

    def test_runtime_audit_denies_paths_outside_stage_and_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            audit = child.RuntimeAudit(temporary, "producer")
            with self.assertRaisesRegex(PermissionError, "runtime audit denied open"):
                audit.check_path("open", "/Volumes/Volume/not-in-stage.json")
            self.assertEqual(audit.denied_events[0]["event"], "open")

    def test_parent_rejects_minimal_child_authored_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "receipt boundary changed"):
                parent.validate_child_runtime_receipt(
                    {"role": "producer", "stage_sha256": "0" * 64, "valid": True},
                    backend_expectations={},
                    role="producer",
                    runtime_boundary={},
                    stage_rows=[],
                    stage_sha256="0" * 64,
                    static_audit_sha256="1" * 64,
                    stage_root=root,
                )

    def test_parent_binds_backend_values_to_execution_matrix(self) -> None:
        expected = {field: field for field in parent.BACKEND_CHECK_FIELDS}
        expected["numpy_distribution_file_count"] = 1320
        expected["os_loader_dependencies_loaded"] = True
        expected["thread_count"] = 1
        attestation = {
            "checks": [
                {
                    "expected": expected[field],
                    "field": field,
                    "match": True,
                    "observed": expected[field],
                }
                for field in parent.BACKEND_CHECK_FIELDS
            ],
            "valid": True,
        }
        parent.validate_child_backend_attestation(attestation, expected)

        forged = copy.deepcopy(attestation)
        forged["checks"][0]["expected"] = "child-forged"
        forged["checks"][0]["observed"] = "child-forged"
        with self.assertRaisesRegex(ValueError, "backend value changed"):
            parent.validate_child_backend_attestation(forged, expected)

    def test_parent_rejects_post_copy_pre_snapshot_mutation(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-target-approved-manifest-",
                dir="/Volumes/Volume/autolab/tmp",
            )
        )
        try:
            approved: list[dict[str, object]] = []
            for name in parent.expected_stage_names("producer"):
                payload = name.encode("ascii")
                approved.append(
                    parent.stage_retained_payload(
                        root / name,
                        payload,
                        parent.MAX_INPUT_BYTES,
                    )
                )
            parent.remove_appledouble_files(root)
            target = root / "run_tt_target_partition.py"
            target.write_bytes(b"X" * target.stat().st_size)
            parent.remove_appledouble_files(root)
            observed = parent.collect_stage_rows(root, "producer")

            with self.assertRaisesRegex(RuntimeError, "parent-retained approved bytes"):
                parent.validate_approved_stage_manifest(approved, observed)
        finally:
            shutil.rmtree(root)

    def test_os_sandbox_denies_network_fork_and_file_writes(self) -> None:
        boundary = self.runtime_boundary(
            [
                {"kind": "literal", "path": "/"},
                {"kind": "subpath", "path": str(Path(sys.base_prefix).resolve())},
            ]
        )
        profile = parent.sandbox_profile(
            Path("/Volumes/Volume/autolab/tmp/example-stage"),
            [{"path": "allowed.txt"}],
            boundary,
        )

        self.assertIn("(deny network*)", profile)
        self.assertIn("(deny process-fork)", profile)
        self.assertIn("(deny file-write*)", profile)
        self.assertIn("(deny file-read-data", profile)
        self.assertIn("(require-not (require-any", profile)

    @unittest.skipUnless(sys.platform == "darwin", "Seatbelt is macOS-specific")
    def test_os_sandbox_denies_file_data_outside_runtime_and_stage(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-target-sandbox-test-",
                dir="/Volumes/Volume/autolab/tmp",
            )
        )
        try:
            stage = root / "stage"
            stage.mkdir()
            allowed = stage / "allowed.txt"
            unlisted = stage / "unlisted.txt"
            forbidden = root / "forbidden.txt"
            runtime = root / "runtime"
            excluded = runtime / "site-packages"
            runtime.mkdir()
            excluded.mkdir()
            allowed_runtime = runtime / "stdlib.txt"
            excluded_runtime = excluded / "other-package.txt"
            allowed.write_text("allowed", encoding="ascii")
            unlisted.write_text("unlisted", encoding="ascii")
            forbidden.write_text("forbidden", encoding="ascii")
            allowed_runtime.write_text("runtime", encoding="ascii")
            excluded_runtime.write_text("excluded", encoding="ascii")
            boundary = self.runtime_boundary(
                [
                    {"kind": "literal", "path": "/"},
                    {
                        "kind": "subpath",
                        "path": str(Path(sys.base_prefix).resolve()),
                    },
                    {"kind": "literal", "path": str(Path(sys.executable).absolute())},
                    {"kind": "literal", "path": str(Path(sys.executable).resolve())},
                    {
                        "excluded_path": str(excluded),
                        "kind": "subpath_excluding",
                        "path": str(runtime),
                    },
                    {"kind": "literal", "path": str(excluded)},
                ]
            )
            profile = parent.sandbox_profile(
                stage,
                [{"path": allowed.name}],
                boundary,
            )
            base_command = [
                "/usr/bin/sandbox-exec",
                "-p",
                profile,
                sys.executable,
                "-I",
                "-B",
                "-c",
                "open(__import__('sys').argv[1], encoding='ascii').read()",
            ]

            allowed_run = subprocess.run(
                [*base_command, str(allowed)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            forbidden_run = subprocess.run(
                [*base_command, str(forbidden)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            unlisted_run = subprocess.run(
                [*base_command, str(unlisted)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            allowed_runtime_run = subprocess.run(
                [*base_command, str(allowed_runtime)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            excluded_runtime_run = subprocess.run(
                [*base_command, str(excluded_runtime)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            system_forbidden_run = subprocess.run(
                [*base_command, "/etc/hosts"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(allowed_run.returncode, 0)
            self.assertEqual(allowed_runtime_run.returncode, 0)
            self.assertNotEqual(forbidden_run.returncode, 0)
            self.assertNotEqual(unlisted_run.returncode, 0)
            self.assertNotEqual(excluded_runtime_run.returncode, 0)
            self.assertNotEqual(system_forbidden_run.returncode, 0)
        finally:
            shutil.rmtree(root)

    @unittest.skipUnless(sys.platform == "darwin", "kqueue vnode is macOS-specific")
    def test_supervisor_rejects_transient_stage_namespace_race(self) -> None:
        root = Path(
            tempfile.mkdtemp(
                prefix="tt-target-race-test-",
                dir="/Volumes/Volume/autolab/tmp",
            )
        )
        try:
            stage = root / "stage"
            stage.mkdir()
            for name in parent.expected_stage_names("producer"):
                (stage / name).write_text(name, encoding="ascii")
            parent.remove_appledouble_files(stage)
            transient = stage / "not-in-stage-rows.txt"
            with parent.StageMutationMonitor(stage, "producer") as monitor:
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
            with self.assertRaisesRegex(RuntimeError, "stage mutated"):
                parent.reject_stage_mutations(events)
        finally:
            shutil.rmtree(root)

    @unittest.skipUnless(sys.platform == "darwin", "APFS race control is macOS-specific")
    def test_monitor_setup_rejects_apfs_inode_substitution(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="tt-target-apfs-race-", dir="/private/tmp"))
        try:
            stage = root / "stage"
            stage.mkdir()
            for name in parent.expected_stage_names("producer"):
                (stage / name).write_text(name, encoding="ascii")
            target = stage / parent.expected_stage_names("producer")[0]
            replacement = root / "same-bytes-replacement.txt"
            replacement.write_bytes(target.read_bytes())
            real_open = parent.os.open
            substituted = False

            def racing_open(path: object, flags: int, *args: object) -> int:
                nonlocal substituted
                descriptor = real_open(path, flags, *args)
                if Path(path) == target and not substituted:
                    parent.os.replace(replacement, target)
                    substituted = True
                return descriptor

            with mock.patch.object(parent.os, "open", side_effect=racing_open):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "vnode binding changed|stage mutated",
                ):
                    parent.StageMutationMonitor(stage, "producer")
            self.assertTrue(substituted)
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
