#!/usr/bin/env python3
"""Single deterministic implementation/control runner for TASK-20260824-aca034."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from dataclasses import asdict
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
SOURCE = TASK_ROOT / "src" / "coherent_signed_qrom_backend.py"
SPEC = importlib.util.spec_from_file_location("coherent_signed_qrom_backend", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load backend source")
backend = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = backend
SPEC.loader.exec_module(backend)


EXPECTED_UPSTREAM = "b5e4c664de212bdb0981d93d70964a1dca1a0ec9"
PATCH = TASK_ROOT / "integration" / f"upstream-{EXPECTED_UPSTREAM}.patch"
RESULT_CACHE: dict[str, object] = {}


class CoherentSignedQromTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.circuit = backend.build_circuit()

    def test_01_actual_gate_ir_and_coherent_selectors(self) -> None:
        circuit = self.circuit
        self.assertGreater(len(circuit.operations), 0)
        self.assertEqual({op.kind for op in circuit.operations}, {"X", "MCX"})
        self.assertFalse(circuit.arithmetic_metadata["run_time_address_branching"])
        address_wires = set(circuit.registers["address"])
        sign_wire = circuit.registers["sign"][0]
        qrom_terms = [op for op in circuit.operations if op.logical_access == "load"]
        self.assertGreater(len(qrom_terms), 0)
        for operation in qrom_terms:
            self.assertTrue(address_wires.issubset(operation.controls))
            self.assertIn(sign_wire, operation.controls)
        self.assertTrue(any(op.tag == "derive-effective-enable" for op in circuit.operations))
        RESULT_CACHE["ir"] = {
            "operation_count": len(circuit.operations),
            "gate_kinds": sorted({op.kind for op in circuit.operations}),
            "coherent_qrom_terms": len(qrom_terms),
            "runtime_classical_address_branching": False,
        }

    def test_02_operation_order_inverse_and_liveness(self) -> None:
        report = backend.liveness(self.circuit)
        phases = report["phase_intervals_inclusive"]
        ordered = [
            phases["derive_enable"], phases["qrom_load"], phases["arithmetic"],
            phases["qrom_unload"], phases["uncompute_enable"],
        ]
        self.assertEqual(ordered, sorted(ordered))
        self.assertTrue(report["qrom_masks_live_through_arithmetic"])
        self.assertTrue(report["inverse_unload_exact"])
        RESULT_CACHE["liveness"] = report

    def test_03_sparse_exact_amplitudes_and_cleanup(self) -> None:
        report = backend.verify_sparse_action(self.circuit)
        self.assertTrue(report["exact_amplitudes"])
        self.assertTrue(report["label_preservation"])
        self.assertTrue(report["cleanup"])
        self.assertTrue({"O", "A", "-A", "-2A"}.issubset(report["exceptional_branches_seen"]))
        self.assertGreaterEqual(len(report["address_values_seen"]), 2)
        self.assertEqual(report["sign_values_seen"], [0, 1])
        self.assertEqual(report["enabled_values_seen"], [0, 1])
        self.assertEqual(report["zero_digit_values_seen"], [0, 1])
        RESULT_CACHE["sparse_amplitude"] = report

    def test_04_complete_basis_domain(self) -> None:
        report = backend.verify_basis_domain(self.circuit)
        self.assertEqual(report["basis_blocks_checked"], 4 * 2 * 2 * 2 * 7)
        self.assertGreater(report["enabled_nonzero_changes"], 0)
        RESULT_CACHE["basis_domain"] = report

    def test_05_all_known_false_controls_detected_and_semantically_fail(self) -> None:
        controls: dict[str, object] = {}
        for variant in backend.KNOWN_FALSE_IDS:
            broken = backend.make_known_false(self.circuit, variant)
            detected, reasons = backend.detect_known_false(broken, variant)
            self.assertTrue(detected, variant)
            semantic_failure = None
            try:
                backend.verify_basis_domain(broken)
            except AssertionError as exc:
                semantic_failure = str(exc)
            self.assertIsNotNone(semantic_failure, variant)
            controls[variant] = {
                "detected": detected,
                "structural_reasons": list(reasons),
                "semantic_failure": semantic_failure,
            }
        RESULT_CACHE["known_false_controls"] = controls

    def test_06_exact_resource_accounting(self) -> None:
        report = backend.operation_counts(self.circuit)
        gates = report["gate_counts"]
        self.assertEqual(gates["CX"], 0)
        self.assertGreater(gates["X"], 0)
        self.assertGreater(gates["MCX"], 0)
        accesses = report["qrom_accesses"]
        self.assertEqual(accesses["load"], accesses["unload"])
        self.assertEqual(accesses["total"], 2 * accesses["load"])
        self.assertEqual(report["peak_dirty_ancilla"], 0)
        self.assertEqual(report["peak_clean_ancilla"], 12)
        RESULT_CACHE["resource_accounting"] = report


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def upstream_check(upstream_repo: Path) -> dict[str, object]:
    head = subprocess.run(
        ["git", "-C", str(upstream_repo), "rev-parse", "HEAD"],
        check=True, text=True, capture_output=True,
    ).stdout.strip()
    if head != EXPECTED_UPSTREAM:
        raise AssertionError(f"upstream HEAD {head} != {EXPECTED_UPSTREAM}")
    tree = subprocess.run(
        ["git", "-C", str(upstream_repo), "rev-parse", "HEAD^{tree}"],
        check=True, text=True, capture_output=True,
    ).stdout.strip()
    apply_check = subprocess.run(
        ["git", "-C", str(upstream_repo), "apply", "--check", str(PATCH)],
        text=True, capture_output=True,
    )
    if apply_check.returncode:
        raise AssertionError(f"patch apply check failed: {apply_check.stderr.strip()}")
    return {
        "url": "https://github.com/ZeroWang030221/Space-Efficient-Quantum-Algorithm-for-Elliptic-Curve-Discrete-Logarithms-with-Resource-Estimation.git",
        "head": head,
        "tree": tree,
        "patch_apply_check": "pass",
        "patch_sha256": sha256(PATCH),
        "patch_size_bytes": PATCH.stat().st_size,
    }


class RecordingResult(unittest.TextTestResult):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--upstream-repo", type=Path, required=True)
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(CoherentSignedQromTests)
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, resultclass=RecordingResult)
    result = runner.run(suite)
    upstream = upstream_check(args.upstream_repo)
    payload = {
        "schema": "crypto.autoresearch.coherent_signed_qrom_results.v1",
        "task_id": "TASK-20260824-aca034",
        "run_kind": "deterministic_implementation_and_control",
        "scientific_experiment": False,
        "seed": "qec-coherent-qrom-20260824",
        "status": "completed_valid" if result.wasSuccessful() else "failed_implementation",
        "tests": {
            "run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
        },
        "observations": RESULT_CACHE,
        "upstream": upstream,
        "claim_boundary": "implementation/control observations only; no scientific or performance claim",
    }
    args.results.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "tests": payload["tests"], "upstream": upstream}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
