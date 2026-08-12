from __future__ import annotations

import gzip
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = EXPERIMENT_DIR / "src"
sys.path.insert(0, str(SOURCE_DIR))

import tt_supervised_artifact as artifact


def remove_appledouble_fixture_paths(root: Path) -> None:
    for path in root.iterdir():
        if path.name.startswith("._"):
            path.unlink()


def producer_child() -> dict[str, object]:
    return {
        "claim_boundary": {
            "breakthrough_claim": False,
            "ecdlp_improvement_claim": False,
            "index_calculus_claim": False,
            "locator_claim": False,
            "target_specialization_claim": False,
            "toy_restricted_model_bound": True,
        },
        "partition": "source_generator",
        "protocol": artifact.PROTOCOL,
        "schema": "tt-source-compiler-raw-v1",
        "summary": {"source_cells": 1},
        "valid": True,
    }


def parent_receipt(child_bytes: bytes) -> dict[str, object]:
    digest = artifact.sha256_bytes(child_bytes)
    return {
        "artifact_freeze_authorized": False,
        "child": {
            "returncode": 0,
            "stdout_bytes": len(child_bytes),
            "stdout_sha256": digest,
            "timed_out": False,
        },
        "output": {
            "bytes": len(child_bytes),
            "path": "/development/source-result.json",
            "sha256": digest,
        },
        "protocol": artifact.PROTOCOL,
        "role": "producer",
        "schema": artifact.PARENT_RECEIPT_SCHEMA,
        "stage": {"static_audit_sha256": "1" * 64},
        "valid": True,
    }


class SupervisedArtifactTests(unittest.TestCase):
    def make_inputs(self, root: Path) -> tuple[Path, Path, bytes]:
        child_bytes = artifact.canonical_bytes(producer_child())
        receipt_bytes = artifact.canonical_bytes(parent_receipt(child_bytes))
        child_path = root / "child.json"
        receipt_path = root / "receipt.json"
        child_path.write_bytes(child_bytes)
        receipt_path.write_bytes(receipt_bytes)
        return child_path, receipt_path, child_bytes

    def test_package_is_deterministic_and_exactly_recovers_child(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, child_bytes = self.make_inputs(root)
            first = root / "first"
            second = root / "second"
            first_report = artifact.pack_artifact(child_path, receipt_path, first)
            second_report = artifact.pack_artifact(child_path, receipt_path, second)
            self.assertTrue(first_report["valid"])
            self.assertTrue(second_report["valid"])
            self.assertEqual(
                first_report["read_bytes"],
                first_report["input_bytes"] + first_report["written_bytes"],
            )
            self.assertEqual(
                first_report["publication"]["atomic_directory_rename_count"], 1
            )
            self.assertFalse(
                first_report["publication"]["temporary_path_present_after_success"]
            )
            self.assertEqual(
                tuple(sorted(path.name for path in first.iterdir())),
                artifact.ARTIFACT_NAMES,
            )
            for name in artifact.ARTIFACT_NAMES:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            manifest, recovered = artifact.verify_artifact(first)
            self.assertEqual(recovered, child_bytes)
            self.assertEqual(
                manifest["child_result"]["uncompressed_sha256"],
                artifact.sha256_bytes(child_bytes),
            )
            self.assertTrue(manifest["trust_model"]["malicious_host_excluded"])
            self.assertFalse(
                manifest["trust_model"]["generic_runner_supervision_claim"]
            )

    def test_parent_receipt_must_bind_child(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            receipt = artifact.strict_object(receipt_path.read_bytes(), "receipt")
            receipt["output"]["sha256"] = "0" * 64
            receipt_path.write_bytes(artifact.canonical_bytes(receipt))
            with self.assertRaisesRegex(ValueError, "exact child result"):
                artifact.pack_artifact(child_path, receipt_path, root / "package")

    def test_authorities_must_not_assert_stronger_claims(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            child = artifact.strict_object(child_path.read_bytes(), "child")
            child["artifact_freeze_authorized"] = True
            child_bytes = artifact.canonical_bytes(child)
            child_path.write_bytes(child_bytes)
            receipt_path.write_bytes(artifact.canonical_bytes(parent_receipt(child_bytes)))
            with self.assertRaisesRegex(ValueError, "forbidden authority"):
                artifact.pack_artifact(child_path, receipt_path, root / "child-package")

            child = producer_child()
            child["claim_boundary"]["campaign_execution_authorized"] = True
            child_bytes = artifact.canonical_bytes(child)
            child_path.write_bytes(child_bytes)
            receipt_path.write_bytes(artifact.canonical_bytes(parent_receipt(child_bytes)))
            with self.assertRaisesRegex(ValueError, "forbidden authority"):
                artifact.pack_artifact(child_path, receipt_path, root / "claim-package")

            child_bytes = artifact.canonical_bytes(producer_child())
            child_path.write_bytes(child_bytes)
            receipt = parent_receipt(child_bytes)
            receipt["generic_runner_supervision_claim"] = True
            receipt_path.write_bytes(artifact.canonical_bytes(receipt))
            with self.assertRaisesRegex(ValueError, "forbidden authority"):
                artifact.pack_artifact(child_path, receipt_path, root / "receipt-package")

            child = producer_child()
            child["summary"]["campaign_execution_authorized"] = True
            child_bytes = artifact.canonical_bytes(child)
            child_path.write_bytes(child_bytes)
            receipt_path.write_bytes(artifact.canonical_bytes(parent_receipt(child_bytes)))
            with self.assertRaisesRegex(ValueError, "forbidden authority"):
                artifact.pack_artifact(child_path, receipt_path, root / "nested-child")

            child_bytes = artifact.canonical_bytes(producer_child())
            child_path.write_bytes(child_bytes)
            receipt = parent_receipt(child_bytes)
            receipt["stage"]["generic_runner_supervision_claim"] = True
            receipt_path.write_bytes(artifact.canonical_bytes(receipt))
            with self.assertRaisesRegex(ValueError, "forbidden authority"):
                artifact.pack_artifact(child_path, receipt_path, root / "nested-receipt")

    def test_trailing_gzip_member_rejects_even_with_rebound_manifest(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            package = root / "package"
            artifact.pack_artifact(child_path, receipt_path, package)
            compressed_path = package / "child-result.json.gz"
            compressed = compressed_path.read_bytes() + gzip.compress(
                b"{}\n", compresslevel=9, mtime=0
            )
            compressed_path.write_bytes(compressed)
            manifest_path = package / "envelope-manifest.json"
            manifest = artifact.strict_object(manifest_path.read_bytes(), "manifest")
            manifest["child_result"]["compressed_bytes"] = len(compressed)
            manifest["child_result"]["compressed_sha256"] = artifact.sha256_bytes(
                compressed
            )
            manifest_path.write_bytes(artifact.canonical_bytes(manifest))
            remove_appledouble_fixture_paths(package)
            with self.assertRaisesRegex(ValueError, "trailing member"):
                artifact.verify_artifact(package)

    def test_noncanonical_gzip_rejects_even_with_rebound_manifest(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, child_bytes = self.make_inputs(root)
            package = root / "package"
            artifact.pack_artifact(child_path, receipt_path, package)
            compressed = gzip.compress(child_bytes, compresslevel=1, mtime=1)
            self.assertNotEqual(compressed, artifact.deterministic_gzip(child_bytes))
            compressed_path = package / "child-result.json.gz"
            compressed_path.write_bytes(compressed)
            manifest_path = package / "envelope-manifest.json"
            manifest = artifact.strict_object(manifest_path.read_bytes(), "manifest")
            manifest["child_result"]["compressed_bytes"] = len(compressed)
            manifest["child_result"]["compressed_sha256"] = artifact.sha256_bytes(
                compressed
            )
            manifest_path.write_bytes(artifact.canonical_bytes(manifest))
            remove_appledouble_fixture_paths(package)
            with self.assertRaisesRegex(ValueError, "deterministic canonical gzip"):
                artifact.verify_artifact(package)

    def test_uncompressed_gate_rejects(self) -> None:
        payload = artifact.deterministic_gzip(b"0123456789")
        with self.assertRaisesRegex(ValueError, "byte gate"):
            artifact.bounded_gzip_decompress(payload, 9)

    def test_regular_file_pre_read_gate_rejects(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            path = Path(temporary) / "bounded"
            path.write_bytes(b"12")
            with self.assertRaisesRegex(ValueError, "bounded regular file"):
                artifact.inspect_regular(path, "bounded control", 1)
            with self.assertRaisesRegex(ValueError, "bounded regular file"):
                artifact.read_regular(path, "bounded control", 1)

    def test_trailing_non_gzip_bytes_reject_even_with_rebound_manifest(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            package = root / "package"
            artifact.pack_artifact(child_path, receipt_path, package)
            compressed_path = package / "child-result.json.gz"
            compressed = compressed_path.read_bytes() + b"trailing"
            compressed_path.write_bytes(compressed)
            manifest_path = package / "envelope-manifest.json"
            manifest = artifact.strict_object(manifest_path.read_bytes(), "manifest")
            manifest["child_result"]["compressed_bytes"] = len(compressed)
            manifest["child_result"]["compressed_sha256"] = artifact.sha256_bytes(
                compressed
            )
            manifest_path.write_bytes(artifact.canonical_bytes(manifest))
            remove_appledouble_fixture_paths(package)
            with self.assertRaisesRegex(ValueError, "trailing member or trailing bytes"):
                artifact.verify_artifact(package)

    def test_trust_boundary_downgrade_rejects(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            package = root / "package"
            artifact.pack_artifact(child_path, receipt_path, package)
            manifest_path = package / "envelope-manifest.json"
            manifest = artifact.strict_object(manifest_path.read_bytes(), "manifest")
            manifest["trust_model"]["generic_runner_supervision_claim"] = True
            manifest_path.write_bytes(artifact.canonical_bytes(manifest))
            remove_appledouble_fixture_paths(package)
            with self.assertRaisesRegex(ValueError, "packaged authorities"):
                artifact.verify_artifact(package)

    def test_extra_path_and_symlink_reject(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            package = root / "package"
            artifact.pack_artifact(child_path, receipt_path, package)
            (package / "extra").write_bytes(b"x")
            remove_appledouble_fixture_paths(package)
            with self.assertRaisesRegex(ValueError, "file set changed"):
                artifact.verify_artifact(package)
            (package / "extra").unlink()
            saved = root / "saved-receipt.json"
            shutil.copy2(package / "parent-receipt.json", saved)
            (package / "parent-receipt.json").unlink()
            (package / "parent-receipt.json").symlink_to(saved)
            remove_appledouble_fixture_paths(package)
            with self.assertRaises(OSError):
                artifact.verify_artifact(package)

    def test_appledouble_cleanup_is_closed_and_counted(self) -> None:
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temporary:
            root = Path(temporary)
            for name in artifact.ARTIFACT_NAMES:
                (root / name).write_bytes(b"authority")
                (root / f"._{name}").write_bytes(b"sidecar")
            metrics = artifact.finalize_private_publication_directory(root)
            self.assertEqual(metrics["appledouble_removed_count"], 3)
            self.assertEqual(metrics["appledouble_removed_logical_bytes"], 21)
            self.assertEqual(
                tuple(sorted(path.name for path in root.iterdir())),
                artifact.ARTIFACT_NAMES,
            )

    def test_pack_read_accounting_matches_instrumented_reads(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            original_read = os.read
            observed = 0

            def counted_read(descriptor: int, amount: int) -> bytes:
                nonlocal observed
                payload = original_read(descriptor, amount)
                observed += len(payload)
                return payload

            with mock.patch.object(artifact.os, "read", side_effect=counted_read):
                report = artifact.pack_artifact(
                    child_path, receipt_path, root / "package"
                )
            self.assertEqual(report["read_bytes"], observed)

    def test_failed_post_publication_verification_removes_destination(self) -> None:
        with tempfile.TemporaryDirectory(
            dir="/Volumes/Volume/autolab/tmp"
        ) as temporary:
            root = Path(temporary)
            child_path, receipt_path, _ = self.make_inputs(root)
            package = root / "package"
            with mock.patch.object(
                artifact,
                "verify_artifact",
                side_effect=ValueError("injected post-publication failure"),
            ):
                with self.assertRaisesRegex(ValueError, "injected post-publication"):
                    artifact.pack_artifact(child_path, receipt_path, package)
            self.assertFalse(package.exists())

    @unittest.skipUnless(sys.platform == "darwin", "hardlink control requires APFS")
    def test_artifact_names_must_not_alias_one_inode(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="tt-supervised-alias-", dir="/private/tmp"))
        try:
            child_path, receipt_path, _ = self.make_inputs(root)
            package = root / "package"
            artifact.pack_artifact(child_path, receipt_path, package)
            receipt = package / "parent-receipt.json"
            receipt.unlink()
            os.link(package / "child-result.json.gz", receipt)
            with self.assertRaisesRegex(ValueError, "alias one inode"):
                artifact.verify_artifact(package)
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
