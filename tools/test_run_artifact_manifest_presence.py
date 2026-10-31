"""Required run companions may use the canonical content-addressed store form."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_ledger as vl


class CanonicalArtifactPresence(unittest.TestCase):
    def test_valid_exact_named_pointer_supplies_presence_without_hydrating(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = {"schema": "artifacts.manifest/v1", "files": {
                "raw-result.json": {"sha256": "a" * 64, "bytes": 10192228}}}
            pointer = root / ".artifacts.json"
            original = json.dumps(raw).encode()
            pointer.write_bytes(original)
            self.assertTrue(vl._artifact_stored(directory, "raw-result.json"))
            self.assertFalse(vl._artifact_stored(directory, "command.txt"))
            self.assertFalse((root / "raw-result.json").exists())
            self.assertEqual(pointer.read_bytes(), original)

    def test_invalid_manifests_cannot_supply_a_required_companion(self):
        invalid = [None, [], {}, {"schema": "wrong", "files": {}},
                   {"schema": "artifacts.manifest/v1", "files": []}]
        for entry in [None, [], {}, {"sha256": "bad", "bytes": 1},
                      {"sha256": "A" * 64, "bytes": 1},
                      {"sha256": "a" * 64, "bytes": True},
                      {"sha256": "a" * 64, "bytes": -1},
                      {"sha256": "a" * 64, "bytes": 1.5}]:
            invalid.append({"schema": "artifacts.manifest/v1", "files": {"raw-result.json": entry}})
        with tempfile.TemporaryDirectory() as directory:
            pointer = Path(directory) / ".artifacts.json"
            for value in invalid:
                with self.subTest(value=value):
                    pointer.write_text(json.dumps(value))
                    self.assertFalse(vl._artifact_stored(directory, "raw-result.json"))
            for value in ["{", '{"schema":"wrong","schema":"artifacts.manifest/v1","files":{"raw-result.json":{"sha256":"' + "a" * 64 + '","bytes":1}}}']:
                with self.subTest(value=value):
                    pointer.write_text(value)
                    self.assertFalse(vl._artifact_stored(directory, "raw-result.json"))

    def test_existing_local_and_legacy_forms_remain_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            for suffix in vl.ARTIFACT_STORED_FORMS:
                with self.subTest(suffix=suffix):
                    path = Path(directory) / ("raw-result.json" + suffix)
                    path.write_bytes(b"existing stored form")
                    self.assertTrue(vl._artifact_stored(directory, "raw-result.json"))
                    path.unlink()
            self.assertFalse(vl._artifact_stored(directory, "raw-result.json"))

    def test_missing_execution_capture_is_still_a_run_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".artifacts.json").write_text(json.dumps({
                "schema": "artifacts.manifest/v1", "files": {
                    "raw-result.json": {"sha256": "a" * 64, "bytes": 1}}}))
            for name in ["environment.json", "stdout.log", "stderr.log"]:
                (root / name).write_text("original capture\n")
            (root / "manifest.yaml").write_text(json.dumps({"run": {
                "id": "RUN-TEST-001", "experiment_id": "EXP-TEST-001", "status": "completed",
                "code": {"commit": "0" * 40, "command": "python3 driver.py"},
                "environment": {"python": "3.11"}, "inputs": {}, "timing": {},
                "result": {"certificate": {"kind": "none"}}}}))
            context = vl.Ctx(set())
            vl.check_run(str(root / "manifest.yaml"), context, {})
            self.assertTrue(any("missing artifact 'command.txt'" in e for e in context.errors), context.errors)
            self.assertFalse(any("missing artifact 'raw-result.json'" in e for e in context.errors), context.errors)


if __name__ == "__main__":
    unittest.main()
