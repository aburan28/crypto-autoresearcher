"""Synthetic metadata checks only. Never invokes a scientific worksheet."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("worksheet_envelope", HERE / "envelope.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class MetadataControls(unittest.TestCase):
    def test_duplicate_keys_and_nonfinite_json_rejected(self):
        for source in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":1e309}'):
            with self.assertRaises(ValueError):
                M.strict_json(source)

    def test_boolean_numeric_substitution_rejected(self):
        self.assertFalse(M.typed_equal({"x": True}, {"x": 1}))
        self.assertFalse(M.typed_equal([False], [0]))
        self.assertFalse(M.typed_equal(1.0, 1))
        self.assertTrue(M.typed_equal({"a": 1, "b": False}, {"b": False, "a": 1}))
        check = M.compare({"control": True}, [{"field": "control", "value": 1}])
        self.assertFalse(check[0]["passed"])

    def test_negative_nonfinite_boolean_resources_rejected(self):
        for bad in (-1, float("nan"), float("inf"), True, "0"):
            with self.assertRaises(ValueError):
                M.nonnegative(bad, "synthetic")
        M.nonnegative(0, "synthetic")
        M.nonnegative(1.5, "synthetic")

    def test_prediction_failure_does_not_redefine_controls(self):
        synthetic = {"control": 7, "observation": 9}
        controls = M.compare(synthetic, [{"field": "control", "value": 7}])
        predictions = M.compare(synthetic, [{"field": "observation", "value": 11}])
        self.assertTrue(all(x["passed"] for x in controls))
        self.assertFalse(all(x["passed"] for x in predictions))

    def test_nested_field_and_distinct_value_control(self):
        result = M.compare({"rows": [{"a": 2, "b": 3}]}, [
            {"field": "rows.0.a", "value": "rows.0.b", "operator": "not_equals_field"}])
        self.assertTrue(result[0]["passed"])

    def test_write_once_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            M.write(path, {"synthetic": True})
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                M.write(path, {"synthetic": False})
            self.assertEqual(path.read_bytes(), before)

    def test_actual_invocation_normalizes_interpreter_only(self):
        self.assertTrue(M.invocation_equal(["/bin/sh", "x", "--out", "a"],
                                           ["/usr/bin/sh", "x", "--out", "a"]))
        self.assertFalse(M.invocation_equal(["/bin/sh", "x", "--out", "a"],
                                            ["/bin/sh", "x", "--out", "b"]))

    def test_exact_primary_receipt_validation_and_tamper_rejection(self):
        # Fixture is metadata, not a native source executed by this test.
        fixture = HERE / "synthetic-checks" / "metadata-source.txt"
        config = {"routes": {"a": fixture.relative_to(M.ROOT).as_posix()},
                  "compiler": {"path": "/synthetic/compiler", "flags": ["-synthetic"]}}
        with tempfile.TemporaryDirectory() as d:
            directory = Path(d)
            binary = str(directory / ".worksheet-a")
            output = b'{"synthetic_only":true}\n'
            def record(argv, stdout=""):
                return {"argv": argv, "returncode": 0, "started_at": "2026-01-01T00:00:00+00:00",
                        "finished_at": "2026-01-01T00:00:01+00:00", "wall_seconds": 1,
                        "cpu_seconds": 0.1, "peak_rss_bytes": 1024, "stdout": stdout}
            primary = {"route": "a", "source": config["routes"]["a"],
                       "source_sha256": M.digest(fixture), "compiler": config["compiler"],
                       "binary_sha256": "a"*64,
                       "compile": record(["/synthetic/compiler", "-synthetic", config["routes"]["a"], "-o", binary]),
                       "synthetic_control": record([binary,"--self-test"], '{"synthetic_control":true,"frozen_worksheet_executed":false}\n'),
                       "worksheet": record([binary], output.decode()),
                       "wall_seconds": 4, "wrapper_cpu_seconds": 0.1, "total_child_cpu_seconds": 0.3,
                       "wrapper_peak_rss_bytes": 2048, "total_child_peak_rss_bytes": 1024, "started_at": "2026-01-01T00:00:00+00:00",
                       "finished_at": "2026-01-01T00:00:04+00:00"}
            M.validate_primary(primary, config, "a", directory, output)
            for key, value in (("route", "b"), ("source_sha256", "b"*64),
                               ("total_child_cpu_seconds", -1), ("binary_sha256", "wrong")):
                changed = copy.deepcopy(primary)
                changed[key] = value
                with self.assertRaises(ValueError):
                    M.validate_primary(changed, config, "a", directory, output)
            changed = copy.deepcopy(primary)
            changed["worksheet"]["stdout"] = "changed"
            with self.assertRaises(ValueError):
                M.validate_primary(changed, config, "a", directory, output)

    def test_predecessor_identity_and_complete_receipt_binding(self):
        # Entirely synthetic metadata under a temporary directory. No native
        # program, real RUN ID, frozen parameter or scientific result is used.
        with tempfile.TemporaryDirectory() as temporary:
            d = Path(temporary)
            plan = {"experiment_id": "SYNTHETIC", "source_sha256": {}, "specification_sha256": "s"*64}
            trial = {"id": "synthetic-a", "run_id": "SYNTHETIC-A", "finite_worksheet": {"route": "a"},
                     "artifacts": M.ARTIFACTS, "argv": ["synthetic", "{run_dir}"],
                     "check_argv": ["synthetic-check", "{run_dir}"]}
            launch = {"plan_sha256": "p"*64, "trial_id": trial["id"], "run_id": trial["run_id"],
                      "argv": M.expanded(trial["argv"], d), "check_argv": M.expanded(trial["check_argv"], d)}
            environment = {"commit": "c"*40, "source_sha256": {}, "specification_sha256": "s"*64}
            M.write(d/"launch.json", launch)
            M.write(d/"environment.json", environment)
            (d/"command.txt").write_text(__import__("json").dumps(launch["argv"]))
            provenance = {name:M.digest(d/name) for name in ("launch.json","environment.json","command.txt")}
            (d/"primary-output.json").write_text('{"synthetic_only":true}\n')
            observations = {"synthetic_only":True}
            raw = {"schema":"finite-worksheet.raw.v1", "experiment_id":"SYNTHETIC", "run_id":"SYNTHETIC-A",
                   "route":"a", "plan_sha256":"p"*64, "specification_sha256":"s"*64, "source_sha256":{},
                   "scope":"synthetic fixture", "seed":None, "supervisor_provenance_sha256":provenance,
                   "primary_output_sha256":M.digest(d/"primary-output.json"), "observations":observations}
            check = {"schema":"finite-worksheet.independent-check.v1", "measurement_valid":True,
                     "route_agreement":True, "primary_route":"a", "plan_sha256":"p"*64,
                     "source_sha256":{}, "supervisor_provenance_sha256":provenance}
            manifest = {"run":{"id":"SYNTHETIC-A", "experiment_id":"SYNTHETIC", "status":"completed_valid",
                               "code":{"commit":"c"*40}, "result":{"valid":True,"metrics":{"observations":observations}}}}
            M.write(d/"raw-result.json",raw); M.write(d/"independent-check.json",check); M.write(d/"manifest.yaml",manifest)
            for name in ["native-primary.json","certificate.yaml","stdout.log","stderr.log","check.stdout.log","check.stderr.log"]:
                (d/name).write_text('synthetic fixture\n')
            generated = {"launch.json","environment.json","command.txt","stdout.log","stderr.log","check.stdout.log","check.stderr.log"}
            receipt = {"schema":"crypto.autoresearch.trial_receipt.v1", "plan_sha256":"p"*64,
                       "trial_id":"synthetic-a", "run_id":"SYNTHETIC-A", "status":"output_validated",
                       "returncode":0, "check_returncode":0, "authority":{"commit":"c"*40},
                       "artifact_sha256":{name:M.digest(d/name) for name in set(M.ARTIFACTS)|generated}}
            M.write(d/"execution-receipt.json",receipt)
            M.predecessor(d,plan,trial,"p"*64,{"scope":"synthetic fixture"})
            # Even with repaired file hashes, changed raw identity must fail.
            for field,value in [("experiment_id","OTHER"),("run_id","OTHER"),("plan_sha256","q"*64),("specification_sha256","q"*64)]:
                changed = copy.deepcopy(raw); changed[field]=value
                (d/"raw-result.json").write_text(__import__("json").dumps(changed))
                repaired=copy.deepcopy(receipt);repaired["artifact_sha256"]["raw-result.json"]=M.digest(d/"raw-result.json")
                (d/"execution-receipt.json").write_text(__import__("json").dumps(repaired))
                with self.assertRaises(ValueError):
                    M.predecessor(d,plan,trial,"p"*64,{"scope":"synthetic fixture"})
            (d/"raw-result.json").write_text(__import__("json").dumps(raw))
            (d/"execution-receipt.json").write_text(__import__("json").dumps(receipt))
            with self.assertRaises(ValueError):
                M.predecessor(d,plan,trial,"p"*64,{"scope":"synthetic fixture"})


if __name__ == "__main__":
    unittest.main()
