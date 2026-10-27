#!/usr/bin/env python3
"""Synthetic offline conformance checks; no Modal API or ECDLP workload."""
import argparse
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import admission_driver
import build_protocol as builder
import prepare_admission


class ProtocolAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.original = json.loads((builder.ROOT / builder.ORIGINAL).read_bytes())
        self.receipt = {
            "schema": builder.RECEIPT_SCHEMA, "completed": True,
            "source_revision": builder.NATIVE_SOURCE_A, "source_a_revision": builder.NATIVE_SOURCE_A,
            "source_b_revision": "b" * 40, "app_id": "ap-SyntheticUnitFixture", "image_id": "im-SyntheticUnitFixture",
            "runtime": "vm", "block_network": True, "requested_cpu": [2, 2], "requested_memory_mib": [12288, 12288],
            "software_probe": {"returncode": 0}, "compiler_executable_sha256": {"g++": "c" * 64},
            **{key: "d" * 64 for key in ("source_a_tree_sha256", "source_b_tree_sha256", "adapter_manifest_sha256",
                                         "context_manifest_sha256", "build_info_sha256", "binary_sha256")},
        }
        self.info = {"schema": "classical.ecdlp.endpoint-reuse.image-build/v1", "source_revision": builder.NATIVE_SOURCE_A,
                     "binary_sha256": "d" * 64, "confirmation_inputs_baked": False, "scientific_workload_executed": False,
                     "source_and_public_input_sha256": {"protocol/analysis.py": builder.ANALYSIS_SHA256}}

    def build(self):
        return builder.build(self.original, None, receipt_sha256=None, receipt_binding_path="test/image.json",
                             build_info_binding_path="test/build.json", correction_id="DEC-20261027-cea721", draft=True)

    def test_narrow_scientific_projection_keeps_laws(self):
        changed = self.build()
        self.assertEqual(builder.scientific_projection(changed), builder.scientific_projection(self.original))
        for mutate in (
            lambda p: p["execution"]["retries"].update(max_attempts=2),
            lambda p: p["arms"][0]["instrument"].update(threads=2),
            lambda p: p["extensions"].update(primary_prefix=32),
            lambda p: p["execution"]["placement"].update(child_timeout_seconds=7200),
            lambda p: p["measurement"]["record"].remove("cpu_model"),
        ):
            bad = copy.deepcopy(changed)
            mutate(bad)
            self.assertNotEqual(builder.scientific_projection(bad), builder.scientific_projection(self.original))
        self.assertEqual(changed["freeze"]["status"], "draft")
        self.assertFalse(changed["execution"]["placement"]["all_clocks_wall_valid"])

    def test_source_a_cannot_be_replaced(self):
        builder.validate_receipt(self.receipt, self.info, "d" * 64)
        bad = copy.deepcopy(self.receipt)
        bad["source_revision"] = bad["source_a_revision"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "registered native source A"):
            builder.validate_receipt(bad, self.info, "d" * 64)

    def test_data_bearing_or_wrong_analysis_image_refused(self):
        for key, value in (("schema", "wrong"), ("confirmation_inputs_baked", True),
                           ("scientific_workload_executed", True), ("source_and_public_input_sha256", {})):
            bad = copy.deepcopy(self.info)
            bad[key] = value
            with self.assertRaises(ValueError):
                builder.validate_receipt(self.receipt, bad, "d" * 64)

    def test_transport_bindings_match_frozen_path_and_hash(self):
        protocol = self.build()
        route = protocol["extensions"]["modal_vm_route"]
        route["image_receipt"]["sha256"] = "a" * 64
        route["build_info"]["sha256"] = "b" * 64
        bindings = {key: route[key]["path"] for key in ("image_receipt", "build_info")}
        inputs = {route[key]["path"]: route[key]["sha256"] for key in bindings}
        prepare_admission.validate_transport_binding_paths(protocol, inputs, bindings)
        for name in bindings:
            changed = dict(bindings)
            changed[name] = "different/path.json"
            with self.assertRaisesRegex(ValueError, "frozen protocol"):
                prepare_admission.validate_transport_binding_paths(protocol, inputs, changed)
            changed_inputs = dict(inputs)
            changed_inputs[bindings[name]] = "c" * 64
            with self.assertRaisesRegex(ValueError, "frozen protocol"):
                prepare_admission.validate_transport_binding_paths(protocol, changed_inputs, bindings)

    def test_driver_one_attempt_and_archive_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "run"
            out.mkdir()
            protocol = root / "protocol.json"
            bundle = root / "public.tar.gz"
            protocol.write_text("synthetic-unit-fixture")
            bundle.write_text("synthetic-unit-fixture-no-targets")
            args = argparse.Namespace(out=out, protocol=protocol, public_bundle=bundle, image_receipt=root / "image.json",
                                      inputs_manifest_sha256="e" * 64, run_id="RUN-ECDLP-b883bf")
            def fake_controller(*params):
                target = Path(params[-1])
                target.mkdir()
                record = {"success": True, "engine_command_returncode": 0,
                          "collection": {"complete": True, "engine_returncode": 0},
                          "scientific_workload": "synthetic test only"}
                (target / "controller-receipt.json").write_text(json.dumps(record))
                return record
            with patch.object(admission_driver.controller, "run", side_effect=fake_controller) as call:
                self.assertEqual(admission_driver.run(args), 0)
                self.assertEqual(call.call_count, 1)
            self.assertEqual(admission_driver.check(out), 0)
            raw = json.loads((out / "raw-result.json").read_bytes())
            raw["controller"]["collection"]["complete"] = False
            (out / "raw-result.json").write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError, "controller duplicate"):
                admission_driver.check(out)
            (out / "modal/controller-receipt.json").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "bytes differ"):
                admission_driver.check(out)

    def test_sealed_engine_failure_stays_failed_and_retained(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "run"
            out.mkdir()
            for name in ("protocol.json", "public.tar.gz"):
                (root / name).write_text("synthetic unit fixture; no ECDLP targets")
            args = argparse.Namespace(out=out, protocol=root / "protocol.json", public_bundle=root / "public.tar.gz",
                                      image_receipt=root / "image.json", inputs_manifest_sha256="e" * 64,
                                      run_id="RUN-ECDLP-b883bf")
            def fake_controller(*params):
                target = Path(params[-1])
                target.mkdir()
                record = {"success": False, "engine_command_returncode": 7,
                          "collection": {"complete": True, "engine_returncode": 7}}
                (target / "controller-receipt.json").write_text(json.dumps(record))
                return record
            with patch.object(admission_driver.controller, "run", side_effect=fake_controller) as call:
                self.assertEqual(admission_driver.run(args), 1)
                self.assertEqual(call.call_count, 1)
            self.assertTrue((out / "modal-evidence.tar.gz").is_file())
            self.assertEqual(json.loads((out / "manifest.yaml").read_bytes())["run"]["status"], "failed")
            self.assertEqual(admission_driver.check(out), 1)


if __name__ == "__main__":
    unittest.main()
