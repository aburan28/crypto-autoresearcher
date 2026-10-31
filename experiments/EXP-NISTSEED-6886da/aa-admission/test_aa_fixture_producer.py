#!/usr/bin/env python3
"""Mock-only tests for the public-prime101 non-cohort A/A producer."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aa_fixture_producer", HERE / "aa_fixture_producer.py")
assert SPEC and SPEC.loader
aa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(aa)

CERTIFICATE = b"101 -1 0 101 0 0\n"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def record(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def serial(body: bytes, certificate: bytes | None = None) -> bytes:
    enclosed = b"" if certificate is None else b"__ECPP_CERTIFICATE_BEGIN__\n" + certificate.rstrip(b"\n") + b"\n__ECPP_CERTIFICATE_END__\n"
    return b"__ECPP_INIT_ABI__ 4 4 4\n__ECPP_GUEST_BEGIN__\n" + body + enclosed + b"__ECPP_CHILD_EXIT__ 0 timeout=0\n__ECPP_GUEST_COMPLETE__\n"


class FixtureProducerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.binding = self.root / "binding.json"
        self.payloads = {name: digest(name.encode()) for name in ("runecpp", "checkcertif", "qemu-init", "arithmetic_vectors_v3")}
        self.kernel_bytes, self.image_bytes = b"synthetic kernel", b"synthetic image"
        self.kernel_hash, self.image_hash = digest(self.kernel_bytes), digest(self.image_bytes)
        self.runtime = {"artifacts": [{"logical_path": "runtime/" + name, "sha256": value} for name, value in self.payloads.items()],
                        "kernel": {"kernel_sha256": self.kernel_hash}, "original_data": {"ecpp.DfD": "synthetic-data"}}
        self.inventory = {"kernel": self.kernel_hash, "Data/ecpp.DfD": "synthetic-data"}
        self.manifest = {"schema": "crypto.autoresearch.nistseed_aa_binding.v1", "fixture": aa.FIXTURE,
                         "primary_configuration": aa.PRIMARY, "limits": aa.LIMITS,
                         "bound_sources": aa.BOUND_SOURCES, "runtime_bindings": self.runtime,
                         "rehash_inventory": self.inventory}
        record(self.binding, self.manifest)
        self.original_runtime_inventory = aa._runtime_inventory
        aa._runtime_inventory = lambda: (self.runtime, self.inventory)

    def tearDown(self) -> None:
        aa._runtime_inventory = self.original_runtime_inventory
        self.tmp.cleanup()

    def boundary(self, mutation: str | None = None):
        def write(output: Path, cache: Path) -> None:
            (cache / "vmlinuz-lts").write_bytes(self.kernel_bytes)
            image = cache / "images" / (self.image_hash + ".cpio.gz")
            image.write_bytes(self.image_bytes)
            child = output / "legacy-child"
            prover, checker = child / "prover", child / "checker"
            prover.mkdir(parents=True); checker.mkdir(parents=True)
            cert = CERTIFICATE
            pbody, cbody = b"0: -1 1\nThis number is prime\n", b"0: -1 1\n\n"
            if mutation == "certificate_root": cert = b"103 -1 0 103 0 0\n"
            if mutation == "malformed_certificate": cert = b"101 -1\n"
            if mutation == "empty_certificate": cert = b""
            if mutation == "step_count" and output.name.startswith("left"):
                cert = b"101 -1 1 2 0 0 2 -1 0 2 0 0\n"
            if mutation == "labels": pbody = b"0: -1 1\nThis number is composite\n"
            if mutation == "checker_rejected": cbody = b"0: -1 0\n\n"
            if mutation == "trace" and output.name.startswith("left"): pbody += b"% unexpected synthetic trace\n"
            ps, cs = serial(pbody, cert), serial(cbody)
            if mutation == "step_count" and output.name.startswith("left"): cs = serial(b"0: -1 1\n1: -1 1\n\n")
            if mutation == "invalid_framing": ps = ps.replace(b"__ECPP_GUEST_COMPLETE__\n", b"")
            if mutation == "crlf": ps, cs = ps.replace(b"\n", b"\r\n"), cs.replace(b"\n", b"\r\n")
            for directory, raw, body, count in ((prover, ps, pbody, 1), (checker, cs, cbody, 0)):
                (directory / "serial.raw").write_bytes(raw)
                normalized = raw.replace(b"\r\n", b"\n").decode("utf-8", "replace").encode("utf-8")
                retained_body = normalized.split(b"__ECPP_GUEST_BEGIN__\n", 1)[1].split(b"\n__ECPP_CHILD_EXIT__", 1)[0]
                (directory / "program.stdout").write_bytes(retained_body)
                (directory / "qemu.stderr").write_bytes(b"")
                result = {"vm_valid": True, "qemu_exit": 33, "child_exit": 0, "reason": None,
                          "elapsed_host_seconds": 0.0, "serial_sha256": aa._sha(raw), "certificate_count": count}
                if mutation == "prover_status" and directory == prover: result["child_exit"] = 9
                if mutation == "checker_status" and directory == checker: result["child_exit"] = 9
                if mutation == "timeout" and directory == prover: result.update(qemu_exit=None, reason="host_watchdog")
                if mutation == "vm_valid_inconsistent" and directory == prover: result["vm_valid"] = False
                record(directory / "result.json", result)
                started = {"command": [aa.QEMU, "-machine", "pc,accel=tcg", "-cpu", "max", "-m", "256", "-smp", "1",
                                       "-nodefaults", "-no-user-config", "-display", "none", "-serial", "stdio", "-monitor", "none",
                                       "-nic", "none", "-no-reboot", "-device", "isa-debug-exit,iobase=0xf4,iosize=4", "-kernel",
                                       str(cache / "vmlinuz-lts"), "-initrd", str(image), "-append",
                                       "console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on"],
                           "program_sha256": self.payloads["runecpp"] if directory == prover else self.payloads["checkcertif"],
                           "init_sha256": self.payloads["qemu-init"],
                           "input_sha256": digest(b"101\n") if directory == prover else digest(cert.rstrip(b"\n")),
                           "stdin_sha256": digest(b""), "data_mode": "full" if directory == prover else None,
                           "guest_limit_seconds": aa.LIMITS["prover_guest_seconds"] if directory == prover else aa.LIMITS["checker_guest_seconds"],
                           "host_limit_seconds": aa.LIMITS["prover_host_seconds"] if directory == prover else aa.LIMITS["checker_host_seconds"],
                           "initramfs_sha256": self.image_hash}
                identity_mutations = {
                    "prover_program": (prover, "program_sha256"), "checker_program": (checker, "program_sha256"),
                    "prover_init": (prover, "init_sha256"), "checker_init": (checker, "init_sha256"),
                    "prover_input": (prover, "input_sha256"), "checker_input": (checker, "input_sha256"),
                    "prover_stdin": (prover, "stdin_sha256"), "checker_stdin": (checker, "stdin_sha256"),
                    "prover_data_mode": (prover, "data_mode"), "checker_data_mode": (checker, "data_mode"),
                    "prover_guest_limit": (prover, "guest_limit_seconds"), "checker_guest_limit": (checker, "guest_limit_seconds"),
                    "prover_host_limit": (prover, "host_limit_seconds"), "checker_host_limit": (checker, "host_limit_seconds"),
                    "prover_command": (prover, "command"), "checker_command": (checker, "command"),
                    "prover_initrd": (prover, "initramfs_sha256"), "checker_initrd": (checker, "initramfs_sha256"),
                }
                if mutation in identity_mutations and identity_mutations[mutation][0] == directory:
                    key = identity_mutations[mutation][1]
                    started[key] = ["wrong"] if key == "command" else "wrong"
                record(directory / "started.json", started)
            if mutation != "absent_certificate_file":
                (prover / "certificate.cformat").write_bytes(b"mismatch" if mutation == "mismatched_certificate_file" else cert.rstrip(b"\n"))
            if mutation == "raw_hash":
                (prover / "serial.raw").write_bytes(ps + b"x")
            if mutation == "private_kernel": (cache / "vmlinuz-lts").write_bytes(b"wrong")
            if mutation == "private_image": image.write_bytes(b"wrong")
        return write

    def run_pair(self, mutation: str | None = None, suffix: str = "") -> dict:
        return aa.build_pair(self.root / ("left" + suffix), self.root / ("right" + suffix), self.binding, self.boundary(mutation))

    def test_complete_raw_pair_is_source_derived_and_real_compared(self) -> None:
        result = self.run_pair()
        self.assertEqual(result["comparison"]["mode"], "A/A")
        self.assertTrue(result["comparison"]["equal"])
        self.assertEqual(result["left"]["fixture"], aa.FIXTURE)
        self.assertEqual(result["left"]["classification"], "CONTROL_VALID")
        self.assertEqual(result["named_orders_executed"], 0)
        self.assertFalse(result["legacy_program_executed"])

    def test_destination_must_be_fresh_and_distinct(self) -> None:
        self.run_pair()
        with self.assertRaisesRegex(aa.Refusal, "fresh"):
            self.run_pair()
        with self.assertRaisesRegex(aa.Refusal, "distinct"):
            aa.build_pair(self.root / "same", self.root / "same", self.binding, self.boundary())

    def test_fixture_input_and_runtime_identity_mutations_refuse(self) -> None:
        for field, value in (("fixture", {"id": "cohort-0", "public_input": "101\\n"}),
                             ("fixture", {"id": aa.FIXTURE["id"], "public_input": "103\\n"}),
                             ("runtime_bindings", {}), ("rehash_inventory", {}),
                             ("primary_configuration", {}), ("limits", {}), ("bound_sources", {})):
            changed = dict(self.manifest); changed[field] = value; record(self.binding, changed)
            with self.assertRaises(aa.Refusal): self.run_pair(suffix="-" + field + str(len(str(value))))
            record(self.binding, self.manifest)

    def test_each_raw_validity_failure_refuses(self) -> None:
        for index, mutation in enumerate(("trace", "prover_status", "checker_status", "timeout", "invalid_framing",
                                           "certificate_root", "step_count", "malformed_certificate", "empty_certificate",
                                           "labels", "checker_rejected", "raw_hash", "absent_certificate_file",
                                           "mismatched_certificate_file", "vm_valid_inconsistent")):
            with self.subTest(mutation=mutation), self.assertRaisesRegex(aa.Refusal, "CONTROL_INVALID|equality"):
                self.run_pair(mutation, "-" + str(index))

    def test_crlf_source_serial_normalizes_to_retained_output(self) -> None:
        result = self.run_pair("crlf", "-crlf")
        self.assertTrue(result["comparison"]["equal"])

    def test_each_started_identity_and_private_cache_mutation_refuses(self) -> None:
        mutations = ("prover_program", "checker_program", "prover_init", "checker_init", "prover_input", "checker_input",
                     "prover_stdin", "checker_stdin", "prover_data_mode", "checker_data_mode", "prover_guest_limit",
                     "checker_guest_limit", "prover_host_limit", "checker_host_limit", "prover_command", "checker_command",
                     "prover_initrd", "checker_initrd", "private_kernel", "private_image")
        for index, mutation in enumerate(mutations):
            with self.subTest(mutation=mutation), self.assertRaisesRegex(aa.Refusal, "CONTROL_INVALID"):
                self.run_pair(mutation, "-identity" + str(index))

    def test_pointer_is_refused_before_artifact_store_read(self) -> None:
        candidate = self.root / "payload"
        pointer = candidate.with_name(candidate.name + ".blob.json")
        pointer.write_text("{}", encoding="utf-8")
        class Store:
            GZ, POINTER = ".gz", ".blob.json"
            def __init__(self): self.calls = 0
            def candidates(self, path): return [path, path.with_name(path.name + self.GZ), path.with_name(path.name + self.POINTER), path.with_name(path.name + self.GZ + self.POINTER)]
            def read_bytes(self, path): self.calls += 1; raise AssertionError("must not read/fetch pointer")
        store = Store()
        with self.assertRaisesRegex(aa.Refusal, "pointer"):
            aa._local_payload_bytes(candidate, store)
        self.assertEqual(store.calls, 0)

    def test_identical_invalid_controls_never_compare_equal(self) -> None:
        with self.assertRaisesRegex(aa.Refusal, "CONTROL_INVALID"):
            self.run_pair("malformed_certificate", "-invalid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
