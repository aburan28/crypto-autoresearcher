"""Run resource-vector harness once; write receipt under write scope.

Declared entrypoint (from TASK-20260730-075 directory):
  python3 -m resource_vector_harness.run_harness
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .ledger_checks import (
    check_classification,
    check_forbidden_clearance_flags,
    check_memory_map_status,
    check_mutation_status,
    check_resource_vector_ledger,
)


def main() -> int:
    task_dir = Path(__file__).resolve().parents[1]
    if str(task_dir) not in sys.path:
        sys.path.insert(0, str(task_dir))

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(
        "resource_vector_harness.test_resource_vector"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    ledger = check_resource_vector_ledger()
    memory_map = check_memory_map_status()
    classification = check_classification()
    mutation = check_mutation_status()
    forbidden = check_forbidden_clearance_flags()

    receipt = {
        "task_id": "TASK-20260730-075",
        "batch_id": "BATCH-026",
        "package_id": "FC0-EXT-PKG-SSI-001",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entrypoint": "python3 -m resource_vector_harness.run_harness",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "was_successful": result.wasSuccessful(),
        "ledger_all_field_checks_passed": ledger["all_field_checks_passed"],
        "ledger_package_ok": ledger["package_ok"],
        "resource_vector_status": ledger["resource_vector_status"],
        "memory_map_passed": memory_map["passed"],
        "qm_memory_map_status": memory_map["status_after_batch"],
        "classification_passed": classification["passed"],
        "disposition": classification["disposition"],
        "qm_stopping": classification["qm_stopping"],
        "qm_error": classification["qm_error"],
        "mutation_passed": mutation["passed"],
        "scaffold_mutated": mutation["scaffold_mutated"],
        "forbidden_clearance_flags_absent": forbidden["passed"],
        "curve_isogeny_quantum_circuit_compute": False,
        "numeric_widths_invented": False,
        "tau_invented": False,
        "probabilities_invented": False,
        "security_bits_invented": False,
        "collimation_sieve_apis_invented": 0,
        "query_memory_cleared": False,
        "qm_stopping_cleared": False,
        "qm_memory_map_cleared": False,
    }
    out = task_dir / "resource_vector_harness" / "harness_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
