"""Run composition ledger harness once; write receipt under write scope.

Declared entrypoint (from TASK-20260730-071 directory):
  python3 -m composition_ledger_harness.run_harness
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from .composition_rules import check_composition_structure
from .membership_rules import check_membership_ledger


def main() -> int:
    task_dir = Path(__file__).resolve().parents[1]
    if str(task_dir) not in sys.path:
        sys.path.insert(0, str(task_dir))

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(
        "composition_ledger_harness.test_composition_ledger"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    membership = check_membership_ledger()
    composition = check_composition_structure()

    receipt = {
        "task_id": "TASK-20260730-071",
        "batch_id": "BATCH-025",
        "package_id": "FC0-EXT-PKG-SSI-001",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entrypoint": "python3 -m composition_ledger_harness.run_harness",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "was_successful": result.wasSuccessful(),
        "membership_all_passed": membership["all_membership_checks_passed"],
        "union_members": membership["union_members"],
        "f_sim_maps_to_F": membership["f_sim"]["maps_to_F"],
        "composition_structure_ok": composition["composition_structure_ok"],
        "composition_status": composition["status"],
        "curve_isogeny_quantum_circuit_compute": False,
        "probabilities_invented": False,
        "numeric_error_bounds_invented": False,
        "security_bits_invented": False,
        "tau_invented": False,
        "collimation_sieve_apis_invented": 0,
        "query_memory_cleared": False,
        "qm_stopping_cleared": False,
    }
    out = task_dir / "composition_ledger_harness" / "harness_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
