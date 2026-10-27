"""Mechanical sweep checks with synthetic metadata; no native solver runs."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("new_parameter_sweep_engine", Path(__file__).with_name("engine.py"))
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


def cohort():
    settings, fixtures, targets = {}, {}, {}
    for i in range(64):
        fid = "synthetic-fixture-" + str(i)
        fixtures[fid] = {"fixture_id": fid, "stratum": "ordinary", "p": "8191", "a": "1", "b": "1",
                         "gx": "1", "gy": "1", "r": "4093", "N": "8186", "seed": "10"}
        for rep in range(2):
            cell = fid + "-rep" + str(rep)
            settings[cell] = {"cell_id": cell, "fixture_id": fid, "replicate": str(rep), "dp_bits": "4",
                              "initial_chains": "16", "endpoint_cap": "64", "max_precomp_ops": "1",
                              "max_online_ops": "1", "seed": str(100 + 2*i + rep)}
            targets[cell] = [{"fixture_id": fid, "replicate": str(rep), "target_id": cell + "-t" + str(q),
                              "target_ordinal": str(q), "qx": "0", "qy": "0", "infinity": "1"}
                             for q in range(64)]
    return SimpleNamespace(settings=settings, fixtures=fixtures, targets=targets,
                           nonce_hex="1"*64, protocol_sha256=engine.OLD_PROTOCOL)


class EngineTests(unittest.TestCase):
    def test_exact_integer_parameter_law_and_common_solver_seed(self):
        base = {"cell_id": "dev-rep0", "seed": "18446744073709551615", "fixture_id": "dev", "replicate": "0"}
        fixture = {"r": "245183"}
        default = engine.derive_setting(base, fixture, "dp0_cap4", 0, 4)
        self.assertEqual((default["dp_bits"], default["initial_chains"], default["endpoint_cap"]), (6, 60, 240))
        self.assertEqual(default["max_precomp_ops"], 3940352)
        self.assertEqual(default["max_online_ops"], 135168)
        for variant, shift, mult in engine.VARIANTS:
            setting = engine.derive_setting(base, fixture, variant, shift, mult)
            self.assertEqual(setting["seed"], base["seed"])
            self.assertEqual(setting["endpoint_cap"], setting["initial_chains"]*mult)
        self.assertEqual(base["cell_id"], "dev-rep0")
        with self.assertRaises(ValueError):
            engine.derive_setting(base, fixture, "unsupported", -20, 1)

    def test_schedule_has_one_rho_per_cell_and_every_variant_family_once(self):
        data = cohort()
        schedule = engine.build_schedule(data, "2"*64)
        self.assertEqual(len(schedule), 5248)
        self.assertEqual(len(set(schedule)), 5248)
        self.assertEqual(sum(a == "rho_reference" for _, _, a in schedule), 128)
        for cell in data.settings:
            selected = [(v, a) for c, v, a in schedule if c == cell]
            self.assertEqual(len(selected), 41)
            self.assertEqual(sum(v == "shared" for v, _ in selected), 1)
        self.assertEqual(schedule, engine.build_schedule(data, "2"*64))
        self.assertNotEqual(schedule, engine.build_schedule(data, "3"*64))

    def test_derived_slices_preserve_public_points_and_refuse_extra_private_column(self):
        data = cohort()
        base = next(iter(data.settings))
        setting = engine.derive_setting(data.settings[base], data.fixtures[data.settings[base]["fixture_id"]], "dp0_cap1", 0, 1)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = engine.write_slices(root/"good", data, base, setting, None)
            target = root/"good/targets.tsv"
            self.assertEqual(target.read_bytes(), engine.table_bytes(engine.TARGET_COLUMNS, data.targets[base]))
            self.assertEqual(files["targets.tsv"]["sha256"], engine.sha_file(target))
            data.targets[base][0]["scalar"] = "not-allowed"
            with self.assertRaises(ValueError):
                engine.write_slices(root/"bad", data, base, setting, None)

    def test_frozen_grid_cannot_be_changed_without_invalidating_hash(self):
        protocol = {"schema": "experiment.protocol/v1", "protocol_id": "EXP-ECDLP-f50061",
                    "extensions": {"parameter_sweep": {
                        "variants": [{"id": v, "dp_shift": s, "cap_multiplier": c} for v, s, c in engine.VARIANTS],
                        "bl_arms": list(engine.BL_ARMS), "prefixes": list(engine.PREFIXES),
                        "source_input_protocol_sha256": engine.OLD_PROTOCOL, "expected_cells": 128,
                        "targets_per_cell": 64, "source_manifest_sha256": "a"*64}},
                    "execution": {"backend": "modal", "measurement_class": "measurement", "timeout_seconds": 3600,
                        "checkpoint": {"policy": "none"}, "retries": {"max_attempts": 1},
                        "placement": {"runtime": "vm", "block_network": True, "child_timeout_seconds": 3600}}}
        body_hash = engine.digest(engine.canonical(protocol))
        protocol["freeze"] = {"status": "frozen", "protocol_sha256": body_hash, "filed_before_affected_data": True}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"protocol.json"
            path.write_text(json.dumps(protocol))
            self.assertEqual(engine.protocol_read(path)[1], body_hash)
            protocol["extensions"]["parameter_sweep"]["variants"][0]["cap_multiplier"] = 4
            path.write_text(json.dumps(protocol))
            with self.assertRaises(ValueError):
                engine.protocol_read(path)

    def test_unresolved_launch_stops_later_children_without_asserting_zero_attempts(self):
        data = cohort()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            public = root/"public"
            public.mkdir()
            for name in ["inputs-manifest.json", "fixtures.tsv"]:
                (public/name).write_text("synthetic metadata only\n")
            for name in ["protocol.json", "context.json", "source-manifest.json"]:
                (root/name).write_text("{}\n")
            args = SimpleNamespace(out=root/"out", public_root=public, protocol=root/"protocol.json",
                                   provider_context=root/"context.json", source_manifest=root/"source-manifest.json",
                                   binary=root/"never-executed", inputs_manifest_sha256="a"*64)
            wait = mock.Mock(side_effect=RuntimeError("synthetic unresolved helper failure"))
            helper = SimpleNamespace(STOP={"signal": None}, wait_child=wait, utc=lambda: "2000-01-01T00:00:00Z",
                                     host_facts=lambda context: {"synthetic": True}, split_stream=mock.Mock())
            summary = engine.execute(args, {"execution": {"timeout_seconds": 3600,
                                     "placement": {"child_timeout_seconds": 3600}}}, "b"*64,
                                     data, {"source_revision_c": "c"*40, "binary_sha256": "d"*64},
                                     {"app_id": "ap-synthetic", "sandbox_id": "sb-synthetic", "image_id": "im-synthetic"}, helper)
            self.assertEqual(wait.call_count, 1)
            self.assertEqual(summary["attempted"], 0)
            self.assertEqual(summary["attempts_unresolved"], 1)
            self.assertEqual(summary["status_counts"], {"infra_error": 1, "not_attempted": 5247})
            manifest = json.loads((args.out/"algorithm-raw-manifest.json").read_text())
            self.assertEqual(len(manifest["groups"]), 5248)
            self.assertFalse(manifest["complete_native_index"])
            self.assertEqual(len(manifest["unresolved_mutable_paths"]), 3)
            self.assertEqual(manifest["groups"][0]["attempts"], None)
            self.assertTrue(all(g["attempts"] == 0 for g in manifest["groups"][1:]))
            helper.split_stream.assert_not_called()


if __name__ == "__main__":
    unittest.main()
