import importlib.util
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import time
import unittest

spec = importlib.util.spec_from_file_location("envelope", Path(__file__).with_name("lattice_experiment_manifest.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ManifestEnvelopeTests(unittest.TestCase):
    def test_supervisor_metadata_is_used_without_inventing_dirty_state(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "experiments" / "EXP-ENDO-371597" / "runs" / "RUN-ENDO-859fbd"
            p.mkdir(parents=True)
            (p / "launch.json").write_text(json.dumps({"run_id": p.name, "argv": ["python3", "fixture.py"]}))
            (p / "environment.json").write_text(json.dumps({"commit": "fixture_only_commit", "source_sha256": {"fixture.py": "fixture_hash"}}))
            m.write_artifacts({"parameters": {}, "checks": {"fixture": True}}, p, 1729,
                              datetime.now(timezone.utc).isoformat(), time.monotonic(), time.process_time())
            run = json.loads((p / "manifest.yaml").read_text())["run"]
            self.assertEqual(run["code"]["commit"], "fixture_only_commit")
            self.assertIsNone(run["code"]["dirty_tree"])
            self.assertEqual(run["experiment_id"], "EXP-ENDO-371597")
            self.assertEqual(run["result"]["certificate"]["kind"], "none")

    def test_standalone_artifacts_are_development_only_and_write_once(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)
            args = ({"parameters": {}, "checks": {"fixture": True}}, p, 1,
                    datetime.now(timezone.utc).isoformat(), time.monotonic(), time.process_time())
            m.write_artifacts(*args)
            run = json.loads((p / "manifest.yaml").read_text())["run"]
            self.assertEqual(run["status"], "development_only")
            original = (p / "raw-result.json").read_bytes()
            with self.assertRaises(FileExistsError):
                m.write_artifacts(*args)
            self.assertEqual((p / "raw-result.json").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
