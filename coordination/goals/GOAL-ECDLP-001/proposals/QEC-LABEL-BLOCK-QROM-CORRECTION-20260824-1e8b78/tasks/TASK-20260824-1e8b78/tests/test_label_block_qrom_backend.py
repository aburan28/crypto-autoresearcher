#!/usr/bin/env python3
"""Sole deterministic implementation/control runner for TASK-20260824-1e8b78."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

TASK_ROOT = Path(__file__).resolve().parents[1]
SOURCE = TASK_ROOT / "src" / "label_block_qrom_backend.py"
PATCH = TASK_ROOT / "integration" / "upstream-b5e4c664de212bdb0981d93d70964a1dca1a0ec9.patch"
EXPECTED_UPSTREAM = "b5e4c664de212bdb0981d93d70964a1dca1a0ec9"
spec = importlib.util.spec_from_file_location("label_block_qrom_backend", SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load backend")
backend = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = backend
spec.loader.exec_module(backend)
OBSERVATIONS: dict[str, object] = {}


class LabelBlockQromTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.circuit = backend.build_circuit()

    def test_01_direct_sum_structure_and_qrom(self) -> None:
        circuit = self.circuit
        counts = backend.operation_counts(circuit)
        self.assertEqual(circuit.metadata["direct_sum"], "U=sum_l |l><l| tensor T_A(l)")
        self.assertFalse(circuit.metadata["runtime_classical_address_branching"])
        self.assertEqual(counts["arithmetic_mcx_18"], 272)
        self.assertEqual(counts["qrom_accesses"]["logical_loads"], 1)
        self.assertEqual(counts["qrom_accesses"]["logical_uses"], 1)
        self.assertEqual(counts["qrom_accesses"]["logical_unloads"], 1)
        self.assertTrue(counts["qrom_accesses"]["inverse_exact"])
        self.assertEqual(counts["comparison_mcx"], 112)
        OBSERVATIONS["structure"] = counts

    def test_02_complete_basis_domains(self) -> None:
        report = backend.verify_domains(self.circuit)
        self.assertEqual(report["exhaustive_checked"], 4096)
        self.assertEqual(report["exhaustive_failures"], 0)
        self.assertEqual(report["valid_checked"], 224)
        self.assertEqual(report["valid_failures"], 0)
        self.assertEqual(report["exceptional_checked"], 32)
        self.assertEqual(report["exceptional_failures"], 0)
        self.assertEqual(report["invalid_code_changes"], 0)
        OBSERVATIONS["domains"] = report

    def test_03_positive_and_mirror_alias_superpositions(self) -> None:
        positive = backend.alias_control(self.circuit, ((2, 0), (3, 1)))
        negative = backend.alias_control(self.circuit, ((2, 1), (3, 0)))
        self.assertEqual(self.circuit.table[(2, 0)], self.circuit.table[(3, 1)])
        self.assertEqual(self.circuit.table[(2, 1)], self.circuit.table[(3, 0)])
        for report in (positive, negative):
            self.assertEqual(report["failures"], 0)
            self.assertTrue(report["labels_unchanged"])
            self.assertTrue(report["relative_phase_preserved"])
            self.assertTrue(report["work_clean"])
        OBSERVATIONS["alias_superpositions"] = {"positive": positive, "mirror_negative": negative}

    def test_04_payload_row_known_false_double_translates_aliases(self) -> None:
        broken = backend.make_known_false(self.circuit, "KF-PAYLOAD-ROW-ITERATED")
        positive = backend.alias_control(broken, ((2, 0), (3, 1)))
        negative = backend.alias_control(broken, ((2, 1), (3, 0)))
        self.assertEqual(positive["failures"], 2)
        self.assertEqual(negative["failures"], 2)
        OBSERVATIONS["payload_row_known_false"] = {
            "positive": positive,
            "mirror_negative": negative,
            "observed_action": "two copies of each aliased label-block translation",
        }

    def test_05_remaining_known_false_objects_rejected(self) -> None:
        reports = {}
        for variant in backend.KNOWN_FALSE_IDS[1:]:
            report = backend.evaluate_known_false(backend.make_known_false(self.circuit, variant), variant)
            self.assertTrue(report["rejected"], variant)
            reports[variant] = report
        OBSERVATIONS["known_false_controls"] = reports

    def test_06_scalable_liveness_boundary_is_explicit(self) -> None:
        report = backend.operation_counts(self.circuit)["scalable_liveness"]
        self.assertEqual(report["peak_extra_clean"], "2*w+9")
        self.assertFalse(report["hidden_n_bit_register_in_this_record-selection_layer"])
        self.assertTrue(report["leading_3n_plus_log_n_transfer"].startswith("not established"))
        OBSERVATIONS["scalable_liveness"] = report


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def upstream_check(repo: Path) -> dict[str, object]:
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, text=True, capture_output=True).stdout.strip()
    if head != EXPECTED_UPSTREAM:
        raise AssertionError(f"upstream HEAD {head} != {EXPECTED_UPSTREAM}")
    tree = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], check=True, text=True, capture_output=True).stdout.strip()
    checked = subprocess.run(["git", "-C", str(repo), "apply", "--check", str(PATCH)], text=True, capture_output=True)
    if checked.returncode:
        raise AssertionError(checked.stderr.strip())
    return {
        "url": "https://github.com/ZeroWang030221/Space-Efficient-Quantum-Algorithm-for-Elliptic-Curve-Discrete-Logarithms-with-Resource-Estimation.git",
        "head": head,
        "tree": tree,
        "patch_apply_check": "pass",
        "patch_sha256": sha256(PATCH),
        "patch_size_bytes": PATCH.stat().st_size,
        "modified_existing_paths": ["README.md"],
        "new_paths": ["label_block_qrom_backend.py", "test_label_block_qrom_backend.py"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--upstream-repo", type=Path, required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LabelBlockQromTests)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    try:
        upstream = upstream_check(args.upstream_repo)
        upstream_error = None
    except Exception as exc:
        upstream = None
        upstream_error = f"{type(exc).__name__}: {exc}"
    status = "completed_valid" if result.wasSuccessful() and upstream_error is None else "failed_implementation"
    payload = {
        "schema": "crypto.autoresearch.label_block_qrom_results.v1",
        "task_id": "TASK-20260824-1e8b78",
        "run_kind": "deterministic_implementation_and_control",
        "scientific_experiment": False,
        "seed": "qec-label-block-qrom-20260824",
        "status": status,
        "tests": {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped)},
        "observations": OBSERVATIONS,
        "upstream": upstream,
        "upstream_error": upstream_error,
        "claim_boundary": "implementation/control observations only; no scientific, scalable-resource, performance, or research-state claim",
    }
    args.results.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "tests": payload["tests"], "upstream_error": upstream_error}, sort_keys=True))
    return 0 if status == "completed_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
