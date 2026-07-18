from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


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
                    role="producer",
                    stage_rows=[],
                    stage_sha256="0" * 64,
                    static_audit_sha256="1" * 64,
                    python_root=Path(sys.base_prefix),
                    stage_root=root,
                )

    def test_os_sandbox_denies_network_fork_and_file_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = parent.sandbox_profile(
                Path(temporary).resolve(), Path(sys.base_prefix).resolve()
            )

        self.assertIn("(deny network*)", profile)
        self.assertIn("(deny process-fork)", profile)
        self.assertIn("(deny file-write*)", profile)


if __name__ == "__main__":
    unittest.main()
