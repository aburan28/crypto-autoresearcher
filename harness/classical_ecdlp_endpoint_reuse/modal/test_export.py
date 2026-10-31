"""Fixed synthetic export conformance; no native solver, cohort draw or API."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO = STUDY.parents[1]
sys.path.insert(0, str(REPO / "tools"))
import experiment_protocol as ep


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


exporter = module("modal_exporter_software_test", HERE / "export_bundle.py")
original = module("source_A_exporter_software_test", STUDY / "protocol/export_bundle.py")
SOURCE_A = "fe01ccd832832488c58abeef17548b0a8db6035f"
BIG = 2**60 + 3
NONCE = "fixed-software-only-export-fixture"


class ModalExportConformance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.raw = self.root / "raw"
        self.raw.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) + "\n")
        return path

    def frozen_fixture(self):
        value = json.loads((REPO / "experiments/EXP-ECDLP-2b4ff1/protocol.json").read_text())
        provider = {"schema": "classical.ecdlp.endpoint-reuse.modal-provider-context/v1",
                    "provider": "modal", "runtime": "vm", "block_network": True,
                    "app_id": "ap-SoftwareFixture", "image_id": "im-SoftwareFixture",
                    "sandbox_id": "sb-SoftwareFixture", "source_revision": SOURCE_A,
                    "source_a_revision": SOURCE_A, "source_b_revision": "c" * 40,
                    "adapter_revision": "c" * 40, "adapter_manifest_sha256": "d" * 64,
                    "build_info_sha256": "e" * 64, "inputs_manifest_sha256": "f" * 64,
                    "binary_sha256": "b" * 64}
        for arm in value["arms"]:
            arm["instrument"].update(commit=SOURCE_A, binary_sha256="b" * 64)
        value["execution"]["backend"] = "modal"
        value["execution"]["placement"].update(runtime="vm", block_network=True,
            app_id=provider["app_id"], image_id=provider["image_id"])
        value["extensions"]["modal_vm_route"] = {"native_source_a": SOURCE_A,
            "adapter_source_b": provider["source_b_revision"], "adapter_manifest_sha256": provider["adapter_manifest_sha256"],
            "build_info": {"sha256": provider["build_info_sha256"]}}
        value["analysis_plan"]["script"]["path"] = str(STUDY / "protocol/analysis.py")
        value["analysis_plan"]["frozen_before_data"] = True
        value["sample_size"]["preflight_runtime"]["estimated_total_seconds"] = 1
        value["freeze"] = {"status": "frozen", "protocol_sha256": ep.protocol_hash(value),
            "commit": "c" * 40, "frozen_at": "2000-01-01T00:00:00+00:00", "filed_before_affected_data": True}
        provider["protocol_sha256"] = value["freeze"]["protocol_sha256"]
        self.assertEqual(ep.schema_errors(value, "experiment.protocol/v1"), [])
        self.assertEqual(ep.lint_protocol(value), [])
        self.protocol = self.write_json(self.root / "protocol.json", value)
        self.provider = provider
        self.value = value
        self.write_json(self.raw / "provider-context.json", provider)
        self.verification = self.write_json(self.root / "verification.json", {
            "schema": "classical.ecdlp.endpoint-reuse.public-verification.v1", "status": "not_run",
            "verifier_sha256": None, "software_fixture": True})

    def child(self, fixture, rep, arm, ordinal, attempts=1, partial=False):
        cell = f"{fixture}-rep{rep}"
        directory = self.raw / "cells" / cell / arm
        directory.mkdir(parents=True)
        record = {"schema": "classical.ecdlp.endpoint-reuse.child-execution.v1",
            "cell_id": cell, "fixture_id": fixture, "replicate": rep, "arm": arm,
            "solver_seed": exporter.public_seed(self.value["freeze"]["protocol_sha256"], NONCE, fixture, rep, "solver_cell"),
            "source_revision": SOURCE_A, "binary_sha256": "b" * 64,
            "source_b_revision": self.provider["source_b_revision"], "adapter_revision": self.provider["adapter_revision"],
            "protocol_sha256": self.value["freeze"]["protocol_sha256"], "inputs_manifest_sha256": "f" * 64,
            "backend": "modal", "runtime": "vm", "attempts": attempts, "resumed": False,
            "provider_identity": {k: self.provider[k] for k in ("app_id", "sandbox_id", "image_id")},
            "status": "infrastructure_error" if attempts is None else "not_attempted" if attempts == 0 else "invalid_output" if partial else "completed",
            "target_ids": [f"{cell}-software-target-{i:02d}" for i in range(64)],
            "native_spawn_observation": "unresolved" if attempts is None else "not_started" if attempts == 0 else "wait4_reaped_child",
            "clock": {"wall_valid": False, "wall_seconds": None},
            "rusage": None, "started_at": None, "finished_at": None}
        rows = []
        if attempts == 1:
            record["host_before"] = {"cpu_model": "fixed-software-fixture", "affinity_cpus": [0],
                "memory_max": "12288", "kernel": "fixed-software-fixture", "isolation_level": "unknown",
                "contended": None, "isolation_blockers": ["software fixture; no isolation attestation"]}
            record["rusage"] = {"user_seconds": (ordinal + 1) / 1000,
                "system_seconds": 0.125, "maxrss_bytes": 8192 + ordinal,
                "scope": "one whole child, all 64 target slots"}
            raw = directory / "raw.jsonl"
            record["raw_output"] = raw.relative_to(self.raw).as_posix()
            base = {"scope": exporter.analysis.SCOPE, "cell_id": cell, "fixture": fixture,
                    "replicate": rep, "arm": arm}
            rows = [dict(base, row_kind="setup", known_count=1, counters={"group_additions": 7})]
            for i in range(1 if partial else 64):
                row = dict(base, row_kind="target", target_id=f"{cell}-software-target-{i:02d}",
                           target_ordinal=i, status="censored", verified_scalar=None,
                           counters={"group_additions": BIG, "scalar_multiplications": 2})
                if i == 0:
                    row.update({family: {"fixed_counter": BIG + 1}
                                for family in exporter.FAMILIES if family != "counters"})
                rows.append(row)
            raw.write_bytes(b"".join((json.dumps(r) + "\n").encode() for r in rows)
                            + (b'{"incomplete-software-fixture":' if partial else b""))
        self.write_json(directory / "execution.json", record)
        return record, rows

    def seal(self):
        files = [{"path": p.relative_to(self.raw).as_posix(), "bytes": p.stat().st_size,
                  "sha256": exporter.analysis.sha(p)} for p in sorted(self.raw.rglob("*")) if p.is_file()]
        self.manifest = self.write_json(self.raw / "algorithm-raw-manifest.json", {
            "schema": "classical.ecdlp.endpoint-reuse.raw-manifest.v1", "files": files,
            "protocol_sha256": self.value["freeze"]["protocol_sha256"], "inputs_manifest_sha256": "f" * 64,
            "flow": {"planned": 768, "software_fixture": True}})

    def export(self):
        out = self.root / "export.json"
        argv = [str(HERE / "export_bundle.py"), "--protocol", str(self.protocol),
            "--raw-manifest", str(self.manifest), "--verification", str(self.verification),
            "--out", str(out), "--repo-root", str(REPO), "--export-id", "software-fixture",
            "--external-nonce", NONCE]
        with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
            exporter.main()
        return json.loads(out.read_text()), result.exception.code, out

    def test_full_fixed_panel_passes_official_check_export_and_preserves_exact_cost_scope(self):
        self.frozen_fixture()
        first_rows = None
        for i in range(64):
            for rep in range(2):
                for arm in exporter.analysis.ARMS:
                    _, rows = self.child(f"software-fixture-{i:02d}", rep, arm, i * 12 + rep * 6 + exporter.analysis.ARMS.index(arm))
                    first_rows = first_rows or rows
        self.seal()
        result, code, path = self.export()
        self.assertEqual(code, 0)
        self.assertEqual(ep.schema_errors(result, "experiment.export/v1"), [])
        self.assertEqual(len(result["runs"]), 768)
        self.assertEqual(result["backend"], "modal")
        self.assertEqual(result["backend_record"]["observed_target_cases"], 49152)
        self.assertEqual(result["backend_record"]["coverage"]["confirmed_executed_children"], 768)
        self.assertTrue(all(r["worker"] == self.provider["sandbox_id"] for r in result["runs"]))
        self.assertTrue(all(r["measurements"]["wall_valid"] is False for r in result["runs"]))
        self.assertEqual(sum(r["measurements"]["cpu_sys_seconds"] for r in result["runs"]), 768 * 0.125)
        row = result["runs"][0]
        self.assertEqual(row["measurements"]["counted"]["group_additions_m64"], str(7 + BIG * 64))
        for key, expected in original.counter_sequences(first_rows).items():
            self.assertEqual(row["measurements"]["counters"][key], expected)
        check = subprocess.run([sys.executable, "-B", str(REPO / "tools/experiment_protocol.py"),
            "check-export", str(path), "--protocol", str(self.protocol), "--verify-files"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_partial_unresolved_and_unattempted_records_survive_without_fabricated_runs(self):
        self.frozen_fixture()
        self.child("software-fixture-00", 0, "static_small", 0)
        _, prefix = self.child("software-fixture-00", 0, "static_full", 1, partial=True)
        self.child("software-fixture-00", 0, "harvest", 2, attempts=None)
        self.child("software-fixture-00", 0, "rho_reference", 3, attempts=0)
        self.seal()
        # A passing label from another run must never qualify these bytes.
        self.write_json(self.verification, {
            "schema": "classical.ecdlp.endpoint-reuse.public-verification.v1",
            "status": "public_equations_and_trace_pass", "input_sha256": {},
            "target_arm_cases": 65, "verified_case_witnesses": 0,
            "producer_status_counts": {"censored": 65}, "verifier_sha256": "a" * 64,
            "software_fixture": True})
        result, code, path = self.export()
        self.assertEqual(code, 1)
        self.assertEqual(ep.schema_errors(result, "experiment.export/v1"), [])
        self.assertEqual(len(result["runs"]), 2)
        self.assertTrue(all(row["attempts"] == 1 for row in result["runs"]))
        backend = result["backend_record"]
        self.assertEqual(backend["coverage"], {"planned_child_slots": 768, "retained_child_metadata": 4,
            "confirmed_executed_children": 2, "unattempted_children": 1, "unresolved_spawns": 1})
        self.assertEqual(backend["unresolved_execution_metadata"][0]["outcome_class"], "not_completed")
        self.assertIsNone(backend["unresolved_execution_metadata"][0]["attempts"])
        self.assertEqual(len(backend["unattempted_execution_metadata"]), 1)
        self.assertEqual(len(backend["native_stream_findings"]), 1)
        self.assertEqual(len(backend["verification_binding_findings"]), 2)
        self.assertTrue(all(r["verification"]["status"] == "error" and r["exclusion"]["excluded"]
                            for r in result["runs"]))
        partial = next(r for r in result["runs"] if r["arm"] == "static_full")
        self.assertEqual(partial["status"], "infra_error")
        self.assertEqual(partial["outcome_class"], "not_completed")
        self.assertEqual(partial["measurements"]["counted"]["observed_target_cases"], 1)
        self.assertNotIn("group_additions_m64", partial["measurements"]["counted"])
        self.assertEqual(partial["measurements"]["counters"]["native.target.counters.group_additions"], f"[{BIG}]")
        self.assertEqual(exporter.target_metrics(prefix), original.target_metrics(prefix))
        check = subprocess.run([sys.executable, "-B", str(REPO / "tools/experiment_protocol.py"),
            "check-export", str(path), "--protocol", str(self.protocol), "--verify-files"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 1)
        self.assertIn("the protocol plans 768", check.stdout)
        self.assertNotIn("attempts", check.stdout)

    def test_verifier_binding_accepts_original_or_every_exact_part(self):
        raw = self.raw / "cells/software/raw.jsonl"
        raw.parent.mkdir(parents=True)
        raw.write_bytes(b"fixed software-only stream\n")
        item = {"path": raw.relative_to(self.raw).as_posix(), "bytes": raw.stat().st_size,
                "sha256": exporter.analysis.sha(raw)}
        manifest_path = self.raw / "manifest.json"
        passing = {"status": "public_equations_and_trace_pass", "input_sha256": {str(raw): item["sha256"]}}
        self.assertEqual(exporter.verification_binding_findings(passing, manifest_path, {"files": [item]}, [item]), [])
        parts = []
        for i, data in enumerate((b"fixed software-only ", b"stream\n")):
            part = raw.with_name(raw.name + ".parts") / f"part-{i:05d}.bin"
            part.parent.mkdir(exist_ok=True)
            part.write_bytes(data)
            parts.append({"path": part.relative_to(self.raw).as_posix(), "bytes": len(data),
                          "sha256": exporter.analysis.sha(part)})
        passing["input_sha256"] = {str(self.raw / p["path"]): p["sha256"] for p in parts}
        self.assertEqual(exporter.verification_binding_findings(passing, manifest_path, {"files": [item, *parts]}, [item]), [])
        passing["input_sha256"].pop(str(self.raw / parts[-1]["path"]))
        self.assertEqual(len(exporter.verification_binding_findings(passing, manifest_path, {"files": [item, *parts]}, [item])), 1)


if __name__ == "__main__":
    unittest.main()
