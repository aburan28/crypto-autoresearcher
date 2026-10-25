#!/usr/bin/env python3
"""Static/mock-only integration tests for TASK-20261024-4f1bf4.

The operator wrapper replaces the original legacy boundary and subprocess APIs
before discovery.  This module injects a complete fake boundary into the real
runner and calls the real independent checker.  It never imports or invokes
cohort_case.execute_case, qemu_controls.vm, a legacy executable, QEMU, or a
subprocess.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


runner = load_module("cohort_runner_under_test", "cohort_runner.py")
checker = load_module("cohort_checker_under_test", "cohort_checker.py")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def framed(body: bytes, child_exit: int = 0, timeout: int = 0) -> bytes:
    return (
        b"__ECPP_INIT_ABI__ 4 4 4\r\n"
        b"__ECPP_GUEST_BEGIN__\r\n"
        + body
        + f"__ECPP_CHILD_EXIT__ {child_exit} timeout={timeout}\r\n".encode("ascii")
        + b"__ECPP_GUEST_COMPLETE__\r\n"
    )


def qemu_result(serial: bytes, *, qemu_exit=33, child_exit=0, reason=None, certificate_count=0):
    return {
        "vm_valid": qemu_exit == 33 and reason is None and child_exit is not None,
        "qemu_exit": qemu_exit,
        "child_exit": child_exit,
        "reason": reason,
        "elapsed_host_seconds": 0.001,
        "serial_sha256": runner.sha_bytes(serial),
        "certificate_count": certificate_count,
    }


class MockedBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.rows, self.runtime = runner.load_cohort()
        self.index = 0
        self.row = self.rows[self.index]
        self.case_number = 0
        self.payload_digests = {Path(item["logical_path"]).name: item["sha256"] for item in self.runtime["artifacts"]}

    def make_case(self):
        self.case_number += 1
        output = self.root / f"run-{self.case_number}"
        output.mkdir()
        binding = self.root / f"binding-{self.case_number}.json"
        manifest = {
            "schema": "crypto.autoresearch.nistseed_ecpp_trial_binding.v1",
            "cohort_index": self.index,
            "output_directory": str(output),
            "frozen_input_sha256": runner.verify_frozen(),
            "limits": runner.LIMITS,
            "primary_configuration": runner.PRIMARY,
        }
        write_json(binding, manifest)
        argv = [
            "python3", "cohort_runner.py", "--index", str(self.index),
            "--output", str(output), "--input-binding-manifest", str(binding),
        ]
        write_json(output / "launch.json", {"argv": argv, "authority": {"task_id": "mock-task", "commit": "0" * 40}})
        write_json(output / "environment.json", {"fixture": "static-mocked", "python": "fixture"})
        (output / "command.txt").write_text(json.dumps(argv) + "\n", encoding="utf-8")
        (output / "stdout.log").write_bytes(b"supervisor stdout is valid provenance\n")
        (output / "stderr.log").write_bytes(b"supervisor stderr is valid provenance\n")
        return output, binding

    def _started(self, program: str, payload: bytes, guest: int, host: int, data_mode=None):
        result = {
            "utc": "2026-10-25T00:00:00+00:00",
            "command": ["/opt/homebrew/bin/qemu-system-i386", "-serial", "stdio"],
            "program_sha256": self.payload_digests[program],
            "init_sha256": self.payload_digests["qemu-init"],
            "initramfs_sha256": "a" * 64,
            "input_sha256": runner.sha_bytes(payload),
            "stdin_sha256": runner.sha_bytes(b""),
            "data_mode": data_mode,
            "guest_limit_seconds": guest,
            "host_limit_seconds": host,
        }
        return result

    def _write_stage(self, directory: Path, program: str, serial: bytes, payload: bytes, guest: int, host: int, *, data_mode=None, certificate_count=0, qemu_exit=33, child_exit=0, reason=None):
        write_json(directory / "started.json", self._started(program, payload, guest, host, data_mode))
        result = qemu_result(
            serial,
            qemu_exit=qemu_exit,
            child_exit=child_exit,
            reason=reason,
            certificate_count=certificate_count,
        )
        write_json(directory / "result.json", result)
        (directory / "serial.raw").write_bytes(serial)
        (directory / "qemu.stderr").write_bytes(b"")
        _, body, _ = runner.guest_parts(serial)
        (directory / "program.stdout").write_bytes(body)
        return result

    def fake_boundary(self, mode="admitted"):
        def fake(index: int, child: Path, cache: Path):
            self.assertEqual(index, self.index)
            self.assertFalse(child.exists())
            self.assertFalse(cache.exists())
            child.mkdir()
            prover = child / "prover"
            prover.mkdir()
            certificate = f"{self.row['n']} -1 0 {self.row['n']} 0 0".encode("ascii")
            include_certificate = mode not in {"missing_certificate", "timeout", "crash"}
            prover_body = (
                b"% Starting phase 1: building the sequence of primes\r\n"
                + f"% N_0={self.row['n']}\r\n".encode("ascii")
                + b"% next D is 15\r\n"
                + b"% D[[0]]=15\r\n"
                + b"This number is prime\r\n"
            )
            if include_certificate:
                if mode == "malformed_certificate":
                    certificate = b"not a certificate"
                prover_body += b"__ECPP_CERTIFICATE_BEGIN__\r\n" + certificate + b"\r\n__ECPP_CERTIFICATE_END__\r\n"
            prover_exit = 0
            qemu_exit = 33
            reason = None
            if mode in {"timeout", "returned_watchdog"}:
                qemu_exit = None
                reason = "host_watchdog"
            if mode == "crash":
                prover_exit = 139
            prover_serial = framed(prover_body, child_exit=prover_exit)
            prover_result = self._write_stage(
                prover,
                "runecpp",
                prover_serial,
                (self.row["n"] + "\n").encode("ascii"),
                300,
                390,
                data_mode="full",
                certificate_count=1 if include_certificate else 0,
                qemu_exit=qemu_exit,
                child_exit=prover_exit,
                reason=reason,
            )
            if include_certificate:
                (prover / "certificate.cformat").write_bytes(certificate)
            observation = {"prover": prover_result, "certificate_admitted": False}
            if mode in {"admitted", "checker_rejection"}:
                checked = child / "checker"
                checked.mkdir()
                accepted = mode == "admitted"
                checker_body = f"  0:     -1 {1 if accepted else 0}       0.00s\r\n".encode("ascii")
                checker_serial = framed(checker_body)
                checker_result = self._write_stage(
                    checked,
                    "checkcertif",
                    checker_serial,
                    certificate,
                    30,
                    90,
                    certificate_count=0,
                )
                observation["checker"] = checker_result
                observation["certificate_admitted"] = accepted
                if accepted:
                    observation["certificate_steps"] = [{"n": int(self.row["n"]), "D": -1, "h": 0, "pratt": [int(self.row["n"])]}]
                    observation["certificate_sha256"] = runner.sha_bytes(certificate)
            if mode == "early_exception":
                raise TimeoutError("mocked failure before child directory creation")
            if mode in {"timeout", "crash", "partial_trace"}:
                raise TimeoutError(f"mocked retained {mode} after raw prover capture")
            return observation
        return fake

    def run_fixture(self, mode="admitted"):
        output, binding = self.make_case()
        fake = self.fake_boundary(mode)
        if mode == "early_exception":
            def early(index, child, cache):
                raise TimeoutError("mocked failure before child directory creation")
            runner.run_trial(self.index, output, binding, early)
        else:
            runner.run_trial(self.index, output, binding, fake)
        return output, binding

    def refresh_inventory(self, output: Path):
        raw = read_json(output / "raw-result.json")
        child = output / "legacy-child"
        raw["driver_artifacts"] = runner.owned_inventory(child) if child.exists() else {}
        write_json(output / "raw-result.json", raw)

    def refresh_supervisor_hash(self, output: Path, name: str):
        raw = read_json(output / "raw-result.json")
        raw["supervisor_artifact_sha256"][name] = runner.sha_file(output / name)
        write_json(output / "raw-result.json", raw)

    def assert_checker_refuses(self, output: Path, reason: str):
        with self.assertRaisesRegex(checker.CheckFailure, reason):
            checker.check(output)

    def test_full_driver_then_independent_checker_accepts_fake_admitted_output(self):
        output, binding = self.run_fixture()
        raw = read_json(output / "raw-result.json")
        self.assertEqual(raw["named_orders_executed"], 1)
        self.assertEqual((output / "input-binding-manifest.json").read_bytes(), binding.read_bytes())
        self.assertTrue((output / "legacy-child/prover/certificate.cformat").is_file())
        self.assertTrue((output / "legacy-child/checker/program.stdout").is_file())
        verdict = checker.check(output)
        self.assertTrue(verdict["accepted"])
        self.assertEqual(verdict["classification"], "PRIOR_PRIMALITY_EVIDENCE_REQUIRED")

    def test_full_mapping_includes_exact_p224_b_side_other(self):
        mapping = runner.prior_mapping(self.rows)
        independent = checker.independent_prior_map(self.rows)
        uid = "urn:ec-record:1:sha256:db6c3a1e40ae241e8e4fb0695a6e68df7b430c74c4cc0a37e32da95808e4df10"
        expected_b = str(int("b4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4", 16))
        self.assertEqual(len(mapping), 21)
        self.assertEqual(mapping, independent)
        self.assertEqual(mapping[uid]["b"], expected_b)
        self.assertEqual(mapping[uid]["corpus_side"], "other")

    def test_consistent_positive_censored_fixtures_are_accepted(self):
        for mode in ("timeout", "crash", "returned_watchdog", "missing_certificate", "malformed_certificate", "checker_rejection", "partial_trace", "early_exception"):
            with self.subTest(mode=mode):
                output, _ = self.run_fixture(mode)
                verdict = checker.check(output)
                self.assertTrue(verdict["accepted"])
                self.assertEqual(verdict["classification"], "INDETERMINATE")
                if mode in {"timeout", "crash", "returned_watchdog", "partial_trace", "early_exception"}:
                    self.assertTrue((output / "failure.json").is_file())

    def test_corrupted_censored_fixture_is_refused(self):
        output, _ = self.run_fixture("timeout")
        observation = read_json(output / "observation.json")
        observation["prover"]["reason"] = None
        write_json(output / "observation.json", observation)
        self.assert_checker_refuses(output, "primitive status mismatch")

    def test_fresh_fixture_mutations_reach_independent_semantic_joints(self):
        def cases():
            yield "row_uid", lambda output: self._mutate_raw(output, lambda raw: raw["curve"].update(curve_uid="urn:tampered")), "cohort row identity"
            yield "row_order", lambda output: self._mutate_raw(output, lambda raw: raw["curve"].update(n="7")), "cohort row identity"
            yield "row_label", lambda output: self._mutate_raw(
                output,
                lambda raw: raw["curve"].update(
                    label="published" if raw["curve"]["label"] == "omitted" else "omitted"
                ),
            ), "cohort row identity"
            yield "prior_missing", lambda output: self._mutate_raw(output, lambda raw: raw["prior_primality_mapping"].pop(self.row["curve_uid"])), "prior mapping"
            yield "prior_parameter", lambda output: self._mutate_raw(output, lambda raw: raw["prior_primality_mapping"][self.row["curve_uid"]].update(a4="0")), "prior mapping"
            yield "frozen_hash", lambda output: self._mutate_raw(output, lambda raw: raw["frozen_input_sha256"].update({next(iter(raw["frozen_input_sha256"])): "0" * 64})), "frozen/runtime"
            yield "kernel", lambda output: self._mutate_raw(output, lambda raw: raw["kernel"].update(kernel_sha256="0" * 64)), "frozen/runtime"
            yield "limit", lambda output: self._mutate_raw(output, lambda raw: raw["limits"].update(prover_host_seconds=1)), "configuration"
            yield "trace", lambda output: self._mutate_observation(output, lambda observation: observation["trace"]["events"][0].update(source_offset=999)), "serial-derived"
            yield "label", lambda output: self._mutate_observation(output, lambda observation: observation.update(legacy_labels_observation_only=["composite"])), "serial-derived"
            yield "certificate_root", self._mutate_certificate_root, "certificate root/grammar"
            yield "checker_acceptance", self._mutate_checker_acceptance, "raw checker serial body"
        for name, mutate, reason in cases():
            with self.subTest(name=name):
                output, _ = self.run_fixture()
                mutate(output)
                self.assert_checker_refuses(output, reason)

    def _mutate_raw(self, output: Path, mutate):
        raw = read_json(output / "raw-result.json")
        mutate(raw)
        write_json(output / "raw-result.json", raw)

    def _mutate_observation(self, output: Path, mutate):
        observation = read_json(output / "observation.json")
        mutate(observation)
        write_json(output / "observation.json", observation)

    def _mutate_certificate_root(self, output: Path):
        certificate = b"101 -1 0 101 0 0"
        serial_path = output / "legacy-child/prover/serial.raw"
        serial = serial_path.read_bytes().replace(
            f"{self.row['n']} -1 0 {self.row['n']} 0 0".encode("ascii"),
            certificate,
        )
        serial_path.write_bytes(serial)
        (output / "legacy-child/prover/certificate.cformat").write_bytes(certificate)
        _, body, certificates = runner.guest_parts(serial)
        (output / "legacy-child/prover/program.stdout").write_bytes(body)
        result = read_json(output / "legacy-child/prover/result.json")
        result["serial_sha256"] = runner.sha_bytes(serial)
        result["certificate_count"] = len(certificates)
        write_json(output / "legacy-child/prover/result.json", result)
        checker_started = read_json(output / "legacy-child/checker/started.json")
        checker_started["input_sha256"] = runner.sha_bytes(certificate)
        write_json(output / "legacy-child/checker/started.json", checker_started)
        observation = read_json(output / "observation.json")
        observation["prover"] = copy.deepcopy(result)
        observation["certificate_sha256"] = runner.sha_bytes(certificate)
        observation["prover_body_sha256"] = runner.sha_bytes(body)
        observation["prover_certificate_count"] = len(certificates)
        observation["legacy_labels_observation_only"] = [
            item.decode("ascii")
            for item in __import__("re").findall(rb"^(?:% )?This number is (prime|composite)\b", body, __import__("re").M)
        ]
        observation["trace"] = runner.trace(serial)
        write_json(output / "observation.json", observation)
        self.refresh_inventory(output)

    def _mutate_checker_acceptance(self, output: Path):
        serial_path = output / "legacy-child/checker/serial.raw"
        serial = serial_path.read_bytes().replace(b"  0:     -1 1       0.00s", b"  0:     -1 0       0.00s")
        serial_path.write_bytes(serial)
        _, body, _ = runner.guest_parts(serial)
        (output / "legacy-child/checker/program.stdout").write_bytes(body)
        result = read_json(output / "legacy-child/checker/result.json")
        result["serial_sha256"] = runner.sha_bytes(serial)
        write_json(output / "legacy-child/checker/result.json", result)
        observation = read_json(output / "observation.json")
        observation["checker"] = copy.deepcopy(result)
        write_json(output / "observation.json", observation)
        self.refresh_inventory(output)

    def test_manifest_supervisor_status_started_and_inventory_mutations_refuse(self):
        def cases():
            yield "manifest_contents", self._mutate_manifest, "binding manifest contents"
            yield "argv", self._mutate_argv, "supervisor argv"
            yield "program", self._mutate_prover_program, "prover fixed input/program/init"
            yield "init", self._mutate_prover_init, "prover fixed input/program/init"
            yield "input", self._mutate_prover_input, "prover fixed input/program/init"
            yield "result_status", self._mutate_result_status, "primitive status mismatch"
            yield "program_stdout", self._mutate_program_stdout, "program.stdout"
            yield "raw_missing", self._mutate_remove_raw, "lacks required raw artifacts"
        for name, mutate, reason in cases():
            with self.subTest(name=name):
                output, _ = self.run_fixture()
                mutate(output)
                self.assert_checker_refuses(output, reason)

    def _mutate_manifest(self, output: Path):
        manifest = read_json(output / "input-binding-manifest.json")
        manifest["limits"] = {"changed": True}
        write_json(output / "input-binding-manifest.json", manifest)
        raw = read_json(output / "raw-result.json")
        raw["input_binding_manifest_sha256"] = runner.sha_file(output / "input-binding-manifest.json")
        raw["supervisor_manifest"] = manifest
        write_json(output / "raw-result.json", raw)

    def _mutate_argv(self, output: Path):
        argv = ["python3", "wrong.py"]
        (output / "command.txt").write_text(json.dumps(argv) + "\n", encoding="utf-8")
        launch = read_json(output / "launch.json")
        launch["argv"] = argv
        write_json(output / "launch.json", launch)
        self.refresh_supervisor_hash(output, "command.txt")
        self.refresh_supervisor_hash(output, "launch.json")

    def _mutate_prover_program(self, output: Path):
        started = read_json(output / "legacy-child/prover/started.json")
        started["program_sha256"] = "0" * 64
        write_json(output / "legacy-child/prover/started.json", started)
        self.refresh_inventory(output)

    def _mutate_prover_init(self, output: Path):
        started = read_json(output / "legacy-child/prover/started.json")
        started["init_sha256"] = "0" * 64
        write_json(output / "legacy-child/prover/started.json", started)
        self.refresh_inventory(output)

    def _mutate_prover_input(self, output: Path):
        started = read_json(output / "legacy-child/prover/started.json")
        started["input_sha256"] = "0" * 64
        write_json(output / "legacy-child/prover/started.json", started)
        self.refresh_inventory(output)

    def _mutate_result_status(self, output: Path):
        result = read_json(output / "legacy-child/prover/result.json")
        result["child_exit"] = 9
        write_json(output / "legacy-child/prover/result.json", result)
        self.refresh_inventory(output)

    def _mutate_program_stdout(self, output: Path):
        (output / "legacy-child/prover/program.stdout").write_bytes(b"producer-controlled contradiction\n")
        self.refresh_inventory(output)

    def _mutate_remove_raw(self, output: Path):
        (output / "legacy-child/prover/qemu.stderr").unlink()
        self.refresh_inventory(output)

    def test_trace_catalog_raw_offsets_and_d1_special_route(self):
        serial = b"% Starting phase 1: building the sequence of primes\r\n% N_0=101\r\n% next D is 15\r\n% D[[1]]=1\r\n%!% Forced to retry, snif...\r\n"
        extracted = runner.trace(serial)
        self.assertEqual([event["kind"] for event in extracted["events"]], ["phase", "recursive_N", "catalog_D", "stored_D", "retry"])
        self.assertEqual(extracted["events"][1]["source_offset"], len(b"% Starting phase 1: building the sequence of primes\r\n"))
        self.assertEqual(extracted["events"][2]["catalog_positions"][0]["file"], "ecpp.DfD")
        self.assertEqual(extracted["events"][3]["catalog_positions"], [])
        self.assertIn("no ecpp.DfD record", extracted["events"][3]["special_route"])

    def test_aa_requires_complete_noncohort_semantics(self):
        left = {
            "fixture": {"id": "public-synthetic-101", "public_input": "101"},
            "trace": {"events": []},
            "prover": {"elapsed_host_seconds": 1.0, "child_exit": 0},
            "checker": {"temporary_path": "/tmp/one", "child_exit": 0},
            "certificate": {"bytes_sha256": "0" * 64},
            "classification": "INDETERMINATE",
            "labels": [],
            "runtime": {"output_directory": "/tmp/one", "kernel": "fixture"},
        }
        right = copy.deepcopy(left)
        right["prover"]["elapsed_host_seconds"] = 2.0
        right["checker"]["temporary_path"] = "/tmp/two"
        right["runtime"]["output_directory"] = "/tmp/two"
        self.assertTrue(checker.aa_compare(left, right)["equal"])
        right["classification"] = "PRIOR_PRIMALITY_EVIDENCE_REQUIRED"
        with self.assertRaisesRegex(checker.CheckFailure, "semantic mismatch"):
            checker.aa_compare(left, right)
        bad = copy.deepcopy(left)
        bad["fixture"]["curve_uid"] = self.row["curve_uid"]
        with self.assertRaisesRegex(checker.CheckFailure, "non-cohort"):
            checker.aa_compare(left, bad)

    def test_supervisor_complete_manifest_compatibility_uses_only_mock_data(self):
        from tools import experiment_execution as supervisor

        output, _ = self.run_fixture("missing_certificate")
        plan = {
            "experiment_id": "EXP-NISTSEED-6886da",
            "task_id": "TASK-20261024-4f1bf4",
            "approved_by": "DEC-MOCK-000000",
            "hypothesis_id": "H-MOCK-000000",
        }
        trial = {"id": "mock-index-0", "run_id": "RUN-NISTSEED-000000", "parameters": {"fixture": "mock-only"}}
        authority = {"commit": "0" * 40}
        started = datetime(2026, 10, 25, tzinfo=timezone.utc).isoformat()
        completed = supervisor.complete_manifest(
            output,
            plan,
            "mock/trial-plan.json",
            "0" * 64,
            trial,
            authority,
            read_json(output / "launch.json")["argv"],
            ["python3", "cohort_checker.py", "--output", str(output)],
            started,
            started,
        )
        self.assertIn(completed["action"], {"completed", "unchanged"})
        self.assertEqual(supervisor.manifest_schema_errors(output / "manifest.yaml"), [])


if __name__ == "__main__":
    unittest.main()
