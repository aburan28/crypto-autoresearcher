from __future__ import annotations

import copy
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import yaml

from tools import materialize_erank_manual_satisfiability as materializer


class MaterializeErankManualSatisfiabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = materializer.load_source(materializer.SOURCE_PATH)
        cls.document, cls.data = materializer.build_document(cls.source)

    def test_frozen_counts_ranges_and_boundary_keys(self) -> None:
        refs = self.data["refs"]
        descriptors = self.data["descriptors"]
        rows = self.data["rows"]
        self.assertEqual(63, len(refs))
        self.assertEqual("REF-001", refs[0]["ref_id"])
        self.assertEqual("REF-063", refs[-1]["ref_id"])
        self.assertEqual(197, len(descriptors))
        self.assertEqual("SC-001", descriptors[0]["constraint_descriptor_id"])
        self.assertEqual("SC-197", descriptors[-1]["constraint_descriptor_id"])
        self.assertEqual(1872, len(rows))
        self.assertEqual("MS-000001", rows[0]["row_id"])
        self.assertEqual("MS-001872", rows[-1]["row_id"])
        self.assertEqual(materializer.EXPECTED_FIXTURE_TOTALS, dict(Counter(
            row["positive_fixture_id"] for row in rows
        )))
        self.assertEqual(materializer.EXPECTED_KEYWORD_COUNTS, dict(Counter(
            row["keyword"] for row in rows
        )))
        self.assertEqual(
            (
                "https://crypto-autoresearcher.invalid/schema/erank/prime-ideals-v1.json",
                "prime_ideal",
                "/$defs/character_basis_binding_descriptor/oneOf",
                "oneOf",
                "/character_basis_binding",
                "0",
            ),
            materializer.row_key(rows[0]),
        )
        self.assertEqual(
            (
                "https://crypto-autoresearcher.invalid/schema/erank/valuations-v1.json",
                "valuation",
                "/type",
                "type",
                "",
                "",
            ),
            materializer.row_key(rows[-1]),
        )

    def test_rows_are_exactly_twelve_fields_sorted_unique_and_complete(self) -> None:
        rows = self.data["rows"]
        self.assertTrue(all(tuple(row) == materializer.ROW_FIELDS for row in rows))
        keys = [materializer.row_key(row) for row in rows]
        self.assertEqual(sorted(keys), keys)
        self.assertEqual(len(keys), len(set(keys)))
        result = materializer.reconciliation(rows, rows)
        self.assertEqual(
            {
                "expected_application_rows": 1872,
                "actual_application_rows": 1872,
                "missing_rows": 0,
                "duplicate_row_keys": 0,
                "extraneous_rows": 0,
                "success": True,
            },
            result,
        )

        missing = materializer.reconciliation(rows, rows[1:])
        self.assertEqual(1, missing["missing_rows"])
        duplicate = materializer.reconciliation(rows, [*rows, rows[0]])
        self.assertEqual(1, duplicate["duplicate_row_keys"])
        extraneous_row = copy.deepcopy(rows[0])
        extraneous_row["positive_instance_path"] = "/not-present"
        extraneous = materializer.reconciliation(rows, [*rows, extraneous_row])
        self.assertEqual(1, extraneous["extraneous_rows"])

    def test_ref_bindings_and_constraint_descriptors_are_bijectively_linked(self) -> None:
        refs = self.data["refs"]
        descriptors = self.data["descriptors"]
        rows = self.data["rows"]
        ref_ids = {row["ref_id"] for row in refs}
        row_by_id = {row["row_id"]: row for row in rows}
        self.assertEqual(63, len(ref_ids))
        self.assertEqual(197, len({row["mapping_row_id"] for row in descriptors}))
        for descriptor in descriptors:
            self.assertIn(descriptor["ref_id"], ref_ids)
            mapping_row = row_by_id[descriptor["mapping_row_id"]]
            self.assertEqual("$ref", mapping_row["keyword"])
            self.assertEqual(
                descriptor["referenced_schema_path"],
                mapping_row["referenced_schema_path"],
            )

    def test_recursive_no_drift_and_list_order_tamper_detection(self) -> None:
        result = materializer.no_drift_result(self.source, self.document)
        self.assertEqual("PASS", result["result"])
        self.assertEqual(0, result["unauthorized_difference_count"])

        tampered = copy.deepcopy(self.document)
        tampered["repair_specification"]["positive_and_null_controls"]["positive_ids"].reverse()
        tampered_result = materializer.no_drift_result(self.source, tampered)
        self.assertEqual("FAIL", tampered_result["result"])
        self.assertGreater(tampered_result["unauthorized_difference_count"], 0)

        allowed = copy.deepcopy(self.document)
        allowed["repair_specification"]["task_id"] = "TASK-ALLOWED-IDENTITY-CHANGE"
        self.assertEqual("PASS", materializer.no_drift_result(self.source, allowed)["result"])

    def test_two_isolated_filesystem_generations_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_spec = Path(first_dir) / "repair-specification.yaml"
            first_report = Path(first_dir) / "materialization-report.yaml"
            second_spec = Path(second_dir) / "repair-specification.yaml"
            second_report = Path(second_dir) / "materialization-report.yaml"
            command_base = [
                sys.executable,
                str(Path(materializer.__file__).resolve()),
                "--source",
                str(materializer.SOURCE_PATH.resolve()),
            ]
            for seed, specification, report in (
                ("1", first_spec, first_report),
                ("987654321", second_spec, second_report),
            ):
                environment = dict(os.environ)
                environment["PYTHONDONTWRITEBYTECODE"] = "1"
                environment["PYTHONHASHSEED"] = seed
                subprocess.run(
                    [
                        *command_base,
                        "--specification-output",
                        str(specification),
                        "--report-output",
                        str(report),
                    ],
                    check=True,
                    cwd=Path.cwd(),
                    env=environment,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(first_spec.read_bytes(), second_spec.read_bytes())
            self.assertEqual(first_report.read_bytes(), second_report.read_bytes())
            self.assertEqual(
                "repair_specification", next(iter(yaml.safe_load(first_spec.read_bytes())))
            )

    def test_immutable_source_hash_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "changed.yaml"
            changed.write_bytes(materializer.SOURCE_PATH.read_bytes() + b"\n")
            with self.assertRaisesRegex(materializer.MaterializationError, "hash mismatch"):
                materializer.load_source(changed)

    def test_checked_in_artifacts_are_exactly_reproducible(self) -> None:
        specification_bytes, report_bytes, _ = materializer.generate_bytes(self.source)
        self.assertEqual(
            specification_bytes,
            materializer.SPECIFICATION_OUTPUT.read_bytes(),
        )
        self.assertEqual(report_bytes, materializer.REPORT_OUTPUT.read_bytes())

    def test_zero_research_and_zero_approval_boundary(self) -> None:
        record = self.document["repair_specification"]
        materialization = record["materialization"]
        self.assertEqual([], materialization["mathematical_claims"])
        self.assertEqual([], materialization["approvals_conferred"])
        self.assertTrue(all(
            value == 0 for value in materialization["prohibited_work_counts"].values()
        ))
        self.assertFalse(record["executable"])
        self.assertFalse(record["approval_conferred"])
        self.assertEqual([], record["mathematical_claims"])
        self.assertEqual("TASK-20260824-a2464b", record["mandatory_next_gate"]["task"])


if __name__ == "__main__":
    unittest.main()
