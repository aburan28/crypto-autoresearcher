"""Fixed software fixtures only: no target drawing, native solver or provider API."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("endpoint_reuse_modal_engine", HERE / "engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)
original = engine.original


def freeze(value):
    value = json.loads(json.dumps(value))
    value.pop("freeze", None)
    digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    value["freeze"] = {"status": "frozen", "protocol_sha256": digest,
                       "filed_before_affected_data": True}
    return value


def protocol():
    return freeze({"schema": "experiment.protocol/v1", "arms": [
        {"id": arm, "instrument": {"commit": engine.SOURCE_A,
                                    "binary_sha256": "b" * 64, "threads": 1}}
        for arm in original.ARMS], "execution": {"backend": "modal",
        "measurement_class": "measurement", "checkpoint": {"policy": "none"},
        "retries": {"max_attempts": 1}, "timeout_seconds": 3600,
        "placement": {"runtime": "vm", "block_network": True,
                      "child_timeout_seconds": 3600}}})


def context():
    # Clearly synthetic software fixture IDs; never passed to the provider SDK.
    return {"schema": engine.CONTEXT_SCHEMA, "provider": "modal", "runtime": "vm",
            "app_id": "ap-SoftwareFixture", "sandbox_id": "sb-SoftwareFixture",
            "image_id": "im-SoftwareFixture", "block_network": True,
            "requested_cpu": [2, 2], "requested_memory_mib": [12288, 12288],
            "source_revision": engine.SOURCE_A, "source_a_revision": engine.SOURCE_A,
            "source_b_revision": "c" * 40, "adapter_revision": "c" * 40, "binary_sha256": "b" * 64,
            "protocol_sha256": "d" * 64, "inputs_manifest_sha256": "e" * 64,
            "build_info_sha256": "f" * 64, "adapter_manifest_sha256": "0" * 64}


def synthetic_cohort(protocol_hash):
    """Dimension-only text values; not a scientific/public EC cohort."""
    fixtures, settings, targets = {}, {}, {}
    for i in range(64):
        fixture = f"software-fixture-{i:02d}"
        fixtures[fixture] = dict.fromkeys(original.write_cell.__globals__["FIXTURE_COLUMNS"], "0")
        fixtures[fixture]["fixture_id"] = fixture
        for rep in range(2):
            cell = f"{fixture}-rep{rep}"
            settings[cell] = dict.fromkeys(original.write_cell.__globals__["SETTING_COLUMNS"], "0")
            settings[cell].update(cell_id=cell, fixture_id=fixture, replicate=str(rep), seed=str(i * 2 + rep))
            targets[cell] = []
            for ordinal in range(64):
                target = dict.fromkeys(original.write_cell.__globals__["TARGET_COLUMNS"], "0")
                target.update(fixture_id=fixture, replicate=str(rep),
                              target_id=f"{cell}-software-target-{ordinal:02d}", target_ordinal=str(ordinal))
                targets[cell].append(target)
    return SimpleNamespace(fixtures=fixtures, settings=settings, targets=targets,
                           protocol_sha256=protocol_hash, nonce_hex="1" * 64)


class ModalEngineConformance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        engine.STOP["signal"] = None

    def tearDown(self):
        engine.STOP["signal"] = None
        self.temp.cleanup()

    def write_json(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) + "\n")
        return path

    def test_helpers_and_source_A_are_reused_without_guard_replacement(self):
        for name in ("build_schedule", "write_cell", "load_inputs", "wait_child", "shape_check", "split_stream"):
            self.assertIs(getattr(engine, name), getattr(original, name))
        for relative, expected in engine.REUSED_SHA256.items():
            self.assertEqual(engine.sha_file(engine.STUDY_ROOT / relative), expected)
        with self.assertRaises(ValueError):
            original.protocol_read(self.write_json("modal-protocol.json", protocol()))
        engine.protocol_read(self.root / "modal-protocol.json")

    def test_frozen_modal_admission_refuses_tampering_and_wrong_backend(self):
        value = protocol()
        path = self.write_json("protocol.json", value)
        self.assertEqual(engine.protocol_read(path)[1], value["freeze"]["protocol_sha256"])
        value["execution"]["placement"]["runtime"] = "gvisor"
        self.write_json("protocol.json", value)
        with self.assertRaises(ValueError):
            engine.protocol_read(path)
        for key, bad in (("backend", "isolab-k8s"), ("backend", "modal-vm")):
            value = protocol()
            value["execution"][key] = bad
            self.write_json("protocol.json", freeze(value))
            with self.assertRaises(ValueError):
                engine.protocol_read(path)

    def test_provider_context_requires_matching_sdk_identities_and_pins(self):
        value = context()
        path = self.write_json("context.json", value)
        read = lambda: engine.provider_context_read(path, engine.SOURCE_A, "b" * 64, "d" * 64, "e" * 64)
        self.assertEqual(read(), value)
        for key, bad in (("sandbox_id", "pod-123"), ("image_id", "sha256:" + "a" * 64),
                         ("runtime", "gvisor"), ("block_network", False),
                         ("source_revision", "a" * 40), ("inputs_manifest_sha256", "a" * 64),
                         ("adapter_revision", "a" * 40)):
            changed = dict(value, **{key: bad})
            self.write_json("context.json", changed)
            with self.assertRaises(ValueError, msg=key):
                read()

    def image_fixture(self):
        image = self.root / "image"
        for relative in ["modal/engine.py", *engine.REUSED_SHA256]:
            dest = image / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(engine.STUDY_ROOT / relative, dest)
        binary = image / "endpoint_reuse"
        binary.write_bytes(b"fixed software-only placeholder; never executed\n")
        value = context()
        adapter = image / "adapter-manifest.json"
        adapter.write_text(json.dumps({"schema": "classical.ecdlp.endpoint-reuse.modal-adapter-manifest/v1",
            "source_a_revision": engine.SOURCE_A, "source_b_revision": value["source_b_revision"],
            "adapter_revision": value["adapter_revision"],
            "files": {"modal/engine.py": engine.sha_file(image / "modal/engine.py")}}) + "\n")
        files = {p.relative_to(image).as_posix(): engine.sha_file(p) for p in image.rglob("*")
                 if p.is_file() and p != binary}
        info = image / "build-info.json"
        info.write_text(json.dumps({"schema": "classical.ecdlp.endpoint-reuse.image-build/v1",
            "source_revision": engine.SOURCE_A, "binary": str(binary),
            "binary_sha256": engine.sha_file(binary), "confirmation_inputs_baked": False,
            "scientific_workload_executed": False, "source_and_public_input_sha256": files}) + "\n")
        value.update(binary_sha256=engine.sha_file(binary), build_info_path=str(info),
                     build_info_sha256=engine.sha_file(info), adapter_manifest_path=str(adapter),
                     adapter_manifest_sha256=engine.sha_file(adapter))
        return image, binary, value

    def test_frozen_route_must_bind_the_actual_source_B_and_modal_image(self):
        value, provider = protocol(), context()
        value["extensions"] = {"modal_vm_route": {
            "native_source_a": provider["source_a_revision"], "adapter_source_b": provider["source_b_revision"],
            "adapter_manifest_sha256": provider["adapter_manifest_sha256"],
            "build_info": {"sha256": provider["build_info_sha256"]}}}
        value["execution"]["placement"].update(app_id=provider["app_id"], image_id=provider["image_id"])
        engine.protocol_context_bindings(value, provider)
        for key in ("adapter_source_b", "adapter_manifest_sha256"):
            bad = json.loads(json.dumps(value))
            bad["extensions"]["modal_vm_route"][key] = "a" * (40 if key == "adapter_source_b" else 64)
            with self.assertRaises(ValueError):
                engine.protocol_context_bindings(bad, provider)
        bad = json.loads(json.dumps(value))
        bad["execution"]["placement"]["image_id"] = "im-OtherSoftwareFixture"
        with self.assertRaises(ValueError):
            engine.protocol_context_bindings(bad, provider)

    def test_build_readback_binds_all_code_binary_and_adapter_source(self):
        image, binary, value = self.image_fixture()
        engine.verify_build(value, binary, image)
        (image / "modal/engine.py").write_text("altered adapter\n")
        with self.assertRaises(ValueError):
            engine.verify_build(value, binary, image)

    def test_self_consistent_modified_original_helper_still_refused(self):
        image, binary, value = self.image_fixture()
        helper = image / "execution/run_experiment.py"
        helper.write_text(helper.read_text() + "\n# software fixture tamper\n")
        info = json.loads((image / "build-info.json").read_text())
        info["source_and_public_input_sha256"]["execution/run_experiment.py"] = engine.sha_file(helper)
        (image / "build-info.json").write_text(json.dumps(info))
        value["build_info_sha256"] = engine.sha_file(image / "build-info.json")
        with self.assertRaises(ValueError):
            engine.verify_build(value, binary, image)

    def test_adapter_revision_must_match_the_hash_pinned_source_B_closure(self):
        image, binary, value = self.image_fixture()
        manifest = image / "adapter-manifest.json"
        adapter = json.loads(manifest.read_text())
        adapter["source_b_revision"] = "a" * 40
        manifest.write_text(json.dumps(adapter))
        value["adapter_manifest_sha256"] = engine.sha_file(manifest)
        info = json.loads((image / "build-info.json").read_text())
        info["source_and_public_input_sha256"]["adapter-manifest.json"] = engine.sha_file(manifest)
        (image / "build-info.json").write_text(json.dumps(info))
        value["build_info_sha256"] = engine.sha_file(image / "build-info.json")
        with self.assertRaises(ValueError):
            engine.verify_build(value, binary, image)

    def test_guest_facts_are_actual_and_have_no_kubernetes_aliases(self):
        value = engine.host_facts(context())
        self.assertEqual(value["uid"], engine.os.getuid())
        self.assertEqual(value["backend"], "modal")
        self.assertEqual(value["runtime"], "vm")
        self.assertEqual(value["isolation_level"], "unknown")
        self.assertFalse({"pod_uid", "node_name", "job_id"} & set(value))

    def args_and_cohort(self):
        value = protocol()
        args = SimpleNamespace(out=self.root / "outputs", protocol=self.write_json("protocol.json", value),
                               binary=self.root / "never-executed-native-placeholder",
                               binary_sha256="b" * 64, source_revision=engine.SOURCE_A,
                               inputs_manifest_sha256="e" * 64)
        return args, value, synthetic_cohort(value["freeze"]["protocol_sha256"])

    def test_exact_original_call_plan_and_counter_streams_keep_every_failure(self):
        args, value, cohort = self.args_and_cohort()
        expected = original.build_schedule(cohort)
        calls, raw_counters = [], {}

        def fake_child(argv, stdout, stderr, timeout, deadline):
            arm, raw = argv[-2], Path(argv[-1])
            cell = raw.parent.parent.name
            calls.append((cell, arm, argv))
            setting = cohort.settings[cell]
            base = {"schema": original.ROW_SCHEMA, "scope": "classical_ecdlp_endpoint_reuse",
                    "cell_id": cell, "fixture": setting["fixture_id"],
                    "replicate": int(setting["replicate"]), "arm": arm}
            rows = [dict(base, row_kind="fixture_validation"),
                    dict(base, row_kind="setup", known_count=1, counters={"group_additions": 7}),
                    dict(base, row_kind="initial_endpoint", index=0)]
            count = 63 if arm == "harvest_disabled" else 5 if arm in ("static_filled", "harvest", "rho_reference") else 64
            rows += [dict(base, row_kind="target", target_id=t["target_id"],
                          target_ordinal=int(t["target_ordinal"]), status="censored" if arm == "static_full" else "failed",
                          counters={"group_additions": 11, "uncharged_lookup_probes": 13})
                     for t in cohort.targets[cell][:count]]
            data = b"".join((json.dumps(r) + "\n").encode() for r in rows)
            raw.write_bytes(data)
            raw_counters[(cell, arm)] = data
            stdout.write_text(json.dumps({"cells": 1, "targets": 64, "rows": len(rows), "clocks_emitted": False}) + "\n")
            stderr.write_bytes(b"fixed software-only diagnostic\n")
            return {"attempts": 1, "resumed": False, "exitcode": 3 if arm in ("static_filled", "rho_reference") else 0,
                    "termination_reason": "child_timeout" if arm == "harvest" else None,
                    "rusage": {"maxrss_raw": 8, "maxrss_raw_unit": "KiB", "maxrss_bytes": 8192},
                    "clock": {"wall_valid": False}}

        with patch.object(engine, "wait_child", side_effect=fake_child), \
             patch.object(engine, "host_facts", return_value={"software_fixture": True}):
            summary = engine.execute(args, value, cohort.protocol_sha256, cohort, context())
        self.assertEqual([(c, a) for c, a, _ in calls], expected)
        self.assertEqual(len(calls), 768)
        self.assertEqual(summary["attempted"], 768)
        self.assertEqual(summary["attempts_unresolved"], 0)
        self.assertEqual(summary["completed"], 256)
        self.assertEqual(summary["status_counts"], {"completed": 256,
                         "invalid_output": 128, "native_nonzero": 256, "timed_out": 128})
        observed_ids = set()
        for cell, arm, argv in calls:
            record = json.loads((args.out / "cells" / cell / arm / "execution.json").read_text())
            observed_ids.update(record["target_ids"])
            self.assertEqual(record["target_ids"], [t["target_id"] for t in cohort.targets[cell]])
            self.assertFalse(record["clock"]["wall_valid"])
            self.assertEqual(record["retries"], 0)
            self.assertEqual(argv[1], "--run")
            if (cell, arm) in raw_counters:
                raw = Path(argv[-1])
                self.assertEqual(raw.read_bytes(), raw_counters[(cell, arm)])
                parts = record["streams"][raw.relative_to(args.out).as_posix()]["parts"]
                self.assertEqual(b"".join((args.out / p["path"]).read_bytes() for p in parts), raw.read_bytes())
        self.assertEqual(len(observed_ids), 8192)
        first_cell = expected[0][0]
        baseline = original.write_cell(cohort, first_cell, self.root / "original-slice")
        for filename, receipt in baseline.items():
            actual = args.out / "inputs" / first_cell / filename
            self.assertEqual(actual.read_bytes(), Path(receipt["path"]).read_bytes())
        manifest = json.loads((args.out / "algorithm-raw-manifest.json").read_text())
        for item in manifest["files"]:
            self.assertEqual(engine.sha_file(args.out / item["path"]), item["sha256"])

    def test_interruption_retains_all_unattempted_cells_and_target_ids(self):
        args, value, cohort = self.args_and_cohort()
        engine.STOP["signal"] = 15
        with patch.object(engine, "wait_child") as child:
            summary = engine.execute(args, value, cohort.protocol_sha256, cohort, context())
        child.assert_not_called()
        self.assertEqual(summary["status_counts"], {"not_attempted": 768})
        self.assertEqual(summary["attempted"], 0)
        self.assertEqual(summary["attempts_unresolved"], 0)
        records = [json.loads(p.read_text()) for p in args.out.glob("cells/*/*/execution.json")]
        self.assertEqual(len(records), 768)
        self.assertEqual(len({target for row in records for target in row["target_ids"]}), 8192)
        self.assertTrue(all(r["attempts"] == 0 and r["reason"] == "interrupted"
                            and r["clock"]["wall_valid"] is False for r in records))

    def test_unresolved_native_child_stops_every_later_spawn_without_retry(self):
        args, value, cohort = self.args_and_cohort()
        def ambiguous_child(argv, stdout, stderr, timeout, deadline):
            stderr.write_bytes(b"fixed software-only ambiguous helper failure\n")
            raise OSError("fixed software-only failure after a possible spawn")
        with patch.object(engine, "wait_child", side_effect=ambiguous_child) as child, \
             patch.object(engine, "host_facts", return_value={"software_fixture": True}):
            summary = engine.execute(args, value, cohort.protocol_sha256, cohort, context())
        self.assertEqual(child.call_count, 1)
        self.assertEqual(summary["attempted"], 0)
        self.assertEqual(summary["attempts_unresolved"], 1)
        self.assertEqual(summary["launch_stop_reason"], "unresolved_native_child")
        self.assertEqual(summary["status_counts"], {"infrastructure_error": 1, "not_attempted": 767})
        records = [json.loads(p.read_text()) for p in args.out.glob("cells/*/*/execution.json")]
        uncertain = [r for r in records if r["attempts"] is None]
        self.assertEqual(len(uncertain), 1)
        self.assertIsNone(uncertain[0].get("rusage"))
        pending = [r for r in records if r["attempts"] == 0]
        self.assertEqual(len(pending), 767)
        self.assertTrue(all(r["reason"] == "unresolved_native_child" and r["rusage"] is None for r in pending))
        self.assertEqual(len({target for row in records for target in row["target_ids"]}), 8192)


if __name__ == "__main__":
    unittest.main()
